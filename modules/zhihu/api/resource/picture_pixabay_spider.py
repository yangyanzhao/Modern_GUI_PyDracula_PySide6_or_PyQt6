"""
Pixbay图片爬虫
"""
import asyncio
import datetime
import logging
import os
import subprocess
import traceback

import requests
from playwright.async_api import async_playwright

from modules.zhihu.api.functions import current_directory
from modules.zhihu.api.utils.common_utils import find_chrome_path, create_dir, close_browser_by_domain, \
    kill_process_by_port
from db.mysql.mysql_jdbc import select_last_one, insert, select_count, create_pool, close_pool

# 构建目标文件夹的绝对路径
folder_path = os.path.join(current_directory, "pictures")


class PicturePixabaySpider:
    def __init__(self, pool, folder_path: str = folder_path, remote_debugging_port=11001,
                 browser_type: str = "chrome.exe", hide: bool = False):
        self.pool = pool
        self.remote_debugging_port = remote_debugging_port
        self.browser_type = browser_type
        debugging_port = f"--remote-debugging-port={self.remote_debugging_port}"
        CHROME_PATH = f'"{find_chrome_path()}"'
        self.command = f"{CHROME_PATH} {debugging_port}"
        if hide:
            self.command = self.command + " --window-position=10000,10000 "
        self.url = "https://www.iesdouyin.com/share/billboard/"
        self.folder_path = folder_path
        # 创建多级文件夹
        create_dir(self.folder_path)

    def check_do(self) -> bool:
        # 检测是否触发爬虫
        # 检测一下图片数量是不是少于100张
        if len(os.listdir(self.folder_path)) > 100:
            return False
        else:
            return True

    async def run(self, is_check: bool = True):
        if is_check and not self.check_do():
            logging.info("图片数量充足，无需补充")
            return

        logging.info("Pixabay图片爬虫开始")

        logging.info("开始清理页面")
        await close_browser_by_domain(self)
        # 清理端口占用
        logging.info(f"开始清理端口占用，端口: {self.remote_debugging_port}")
        await kill_process_by_port(self.remote_debugging_port)
        # 初始页码
        current_page = 0
        try:
            logging.info(f"启动Chrome进程，命令: {self.command}")
            self.chrome_process = subprocess.Popen(self.command, shell=True)
            # 等WS启动起来
            logging.info("等待Chrome进程启动")
            await asyncio.sleep(5)
            # 检查Chrome进程是否正在运行
            if self.chrome_process.poll() is None:
                logging.info(f"Chrome:{self.remote_debugging_port}进程成功启动")
            else:
                logging.error(f"Chrome:{self.remote_debugging_port}进程启动失败")
                return
            logging.info(f"数据库查询最新页码")
            page_used = await select_last_one(self.pool, table_name='picture_page_used')
            if page_used:
                current_page = page_used['page']
                logging.info(f"最新页码:{current_page}")
            async with async_playwright() as p:
                logging.info(f"连接到Chrome，端口: {self.remote_debugging_port}")
                self.browser = await p.chromium.connect_over_cdp(f"http://localhost:{self.remote_debugging_port}")
                self.content = self.browser.contexts[0]
                self.page = await self.content.new_page()
                # 按ESC键退出升级页面
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")

                self.url = f"https://pixabay.com/zh/photos/search/?pagi={current_page + 1}"
                logging.info(f"导航到URL: {self.url}")

                await self.page.goto(url=self.url, wait_until='commit', timeout=3 * 60 * 1000)
                # 等待页面加载完成
                await self.page.wait_for_load_state(timeout=3 * 60 * 1000)
                logging.info(f"鼠标下滑")
                for i in range(20):
                    await self.page.mouse.wheel(0, 1080)
                    await asyncio.sleep(0.5)
                    await self.page.mouse.wheel(0, -500)
                    await asyncio.sleep(0.5)
                    print(f"下滑:{i}")
                # 按ESC键退出升级页面
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")

                await asyncio.sleep(3)
                # 获取列表
                picture_selector = 'xpath=//img'
                selector_all = await self.page.query_selector_all(picture_selector)

                def get_filename_from_url(url):
                    # 从URL中提取文件名
                    filename_with_extension = os.path.basename(url)
                    # 分割文件名和后缀
                    filename, file_extension = os.path.splitext(filename_with_extension)
                    return filename, file_extension

                for selector in selector_all:
                    url = await selector.get_attribute("src")
                    if url.startswith("https://cdn.pixabay.com"):
                        logging.info(f"保存图片到本地:{url}")
                        logging.info(f"从URL中提取文件名和后缀")
                        filename, file_extension = get_filename_from_url(url)
                        # 构建保存的文件路径
                        save_path = os.path.join(self.folder_path, f"{filename}{file_extension}")
                        logging.info(f"如果已经下载或者使用过了，就不再重复下载")
                        if self.is_exist_or_used_pictures(save_path):
                            logging.info("重复了，跳过该张图片")
                            continue
                        payload = {}
                        headers = {
                            'Upgrade-Insecure-Requests': '1',
                            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
                        }
                        response = requests.request("GET", url, headers=headers, data=payload, timeout=60)
                        if "远程主机强迫关闭了一个现有的连接" in response.text:
                            logging.info(f"远程主机强迫关闭了一个现有的连接,暂停三分钟")
                            await asyncio.sleep(3 * 60)
                            logging.info("休息结束，继续")
                            continue
                        if response.status_code == 200:
                            with open(save_path, 'wb') as file:
                                file.write(response.content)
                            logging.info(f"图片下载成功 and saved to {save_path}")
                        else:
                            logging.info(f"图片下载失败 Status code: {response.content.decode('utf-8')}")
                        await asyncio.sleep(3)

                logging.info(f"当前页{current_page + 1}完成")
                logging.info(f"将页码存储到数据库{current_page + 1}")
                data = {
                    "page": current_page + 1,
                    "datetime": datetime.datetime.now()
                }
                await insert(self.pool, table_name='picture_page_used', data=data)
                await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            traceback.print_exc()
            exc_info = traceback.format_exc()
            logging.error(exc_info)
        finally:
            pass
            try:
                if self.chrome_process and self.chrome_process.poll() is None:
                    self.chrome_process.terminate()
                    self.chrome_process.wait()
            except Exception as e:
                logging.error(f"Failed to terminate Chrome process: {e}")
            try:
                logging.info("清理页面")
                await close_browser_by_domain(self)
                logging.info(f"清理端口占用，端口: {self.remote_debugging_port}")
                await kill_process_by_port(self.remote_debugging_port)
            except Exception as e:
                logging.error(f"Failed to clean up resources: {e}")

    async def run_with_no_end(self):
        logging.info("开始无限爬虫，直到过了每天的凌晨六点钟就停止")

        while True:
            await self.run(is_check=False)

    async def is_exist_or_used_pictures(self, picture_path: str):
        try:
            if picture_path and os.path.exists(picture_path):
                return True
            count = await select_count(self.pool, table_name='used_pictures',
                                       condition=[{'field': 'files_dir', 'value': picture_path, 'op': 'eq'}])

            if picture_path and count != 0:
                return True
        except Exception as e:
            traceback.print_exc()
            exc_info = traceback.format_exc()

    @staticmethod
    async def main_spider():
        # 创建数据库连接池
        pool = await create_pool(db='zhihu')
        try:
            spider = PicturePixabaySpider(pool=pool)
            await spider.run()
        finally:
            pool.close()  # 手动关闭连接
            await pool.wait_closed()  # 等待连接关闭


if __name__ == '__main__':
    # 创建日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logs_dir = fr'logs\{datetime.date.today()}'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    # 创建文件处理器，将日志写入文件
    file_handler = logging.FileHandler(
        filename=os.path.join(logs_dir, f'picture_pixabay_spider_{datetime.date.today()}.log'), mode='a',
        encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    # 创建控制台处理器，将日志输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    # 将处理器添加到日志记录器
    logger.addHandler(file_handler)

    while True:
        asyncio.run(PicturePixabaySpider.main_spider())
