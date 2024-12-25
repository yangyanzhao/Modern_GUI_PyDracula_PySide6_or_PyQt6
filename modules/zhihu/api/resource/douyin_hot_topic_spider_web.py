"""
抖音热点爬虫
2024年9月22日21:55:12 调试通过
"""
import asyncio
import datetime
import logging
import os
import subprocess
import traceback

from playwright.async_api import async_playwright

from modules.zhihu_auto.api.utils.common_utils import find_chrome_path, close_browser_by_domain, kill_process_by_port
from db.mysql.mysql_jdbc import select_count, insert_batch, create_pool


class DouyinHotTopicSpiderWeb:
    def __init__(self, pool, remote_debugging_port=11000, browser_type: str = "chrome.exe"):
        self.remote_debugging_port = remote_debugging_port
        self.browser_type = browser_type
        debugging_port = f"--remote-debugging-port={self.remote_debugging_port}"
        CHROME_PATH = f'"{find_chrome_path()}"'
        self.command = f"{CHROME_PATH} {debugging_port}"
        self.url = "https://www.iesdouyin.com/share/billboard/"
        self.pool = pool

    async def run(self):
        logging.info("抖音热点爬虫开始")

        logging.info("开始清理页面")
        await close_browser_by_domain(self)
        # 清理端口占用
        logging.info(f"开始清理端口占用，端口: {self.remote_debugging_port}")
        await kill_process_by_port(self.remote_debugging_port)

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
            async with async_playwright() as p:
                logging.info(f"连接到Chrome，端口: {self.remote_debugging_port}")
                self.browser = await p.chromium.connect_over_cdp(f"http://localhost:{self.remote_debugging_port}")
                self.content = self.browser.contexts[0]
                self.page = await self.content.new_page()
                # 按ESC键退出升级页面
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")
                logging.info(f"导航到URL: {self.url}")
                await self.page.goto(url=self.url)
                # 等待页面加载完成
                await self.page.wait_for_load_state()
                # 按ESC键退出升级页面
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")

                await asyncio.sleep(3)
                # 获取列表
                file_input_selector = 'xpath=//div[@class="hot-list"]//div[@class="list-container"]/div//div[@class="word"]/span[@class="sentence nowrap"]'
                logging.info(f"获取抖音热点列表")
                selector_all = await  self.page.query_selector_all(file_input_selector)
                logging.info(f"热点循环入库")
                data_list = []
                for selector in selector_all:
                    content = await selector.text_content()
                    count = await select_count(pool=self.pool, table_name='hot_topics',
                                               condition=[{'field': 'topic_name', 'value': content, 'op': 'eq'},
                                                          {'field': 'status', 'value': 0, 'op': 'eq'}])
                    if count == 0:
                        # TODO 这里应该要对热点去搜索一下相关的热点内容。而不是简简单单的标题。
                        d = {
                            'topic_name': str(content),
                            'topic_content': "",
                            'type': "微博热点",
                            'status': 0,
                            'spider_date': datetime.date.today(),
                            'use_date': '2000-01-01',
                            'datetime': datetime.datetime.now()
                        }
                        data_list.append(d)

                if len(data_list) > 0:
                    await insert_batch(pool=self.pool, table_name='hot_topics', data_list=data_list)

                logging.info(f"入库完成")
                logging.info("清理页面")
                await close_browser_by_domain(self)
                logging.info(f"清理端口占用，端口: {self.remote_debugging_port}")
                await kill_process_by_port(self.remote_debugging_port)
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

    @staticmethod
    async def main_spider():
        # 创建数据库连接池
        pool = await create_pool(db='zhihu')
        try:
            spider = DouyinHotTopicSpiderWeb(pool=pool)
            await spider.run()
        finally:
            pool.close()  # 手动关闭连接
            await pool.wait_closed()  # 等待连接关闭


if __name__ == '__main__':
    import nest_asyncio

    # 创建日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logs_dir = fr'logs\{datetime.date.today()}'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    # 创建文件处理器，将日志写入文件
    file_handler = logging.FileHandler(
        filename=os.path.join(logs_dir, f'douyin_hot_topic_spider_{datetime.date.today()}.log'), mode='a',
        encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    # 创建控制台处理器，将日志输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    # 将处理器添加到日志记录器
    logger.addHandler(file_handler)

    nest_asyncio.apply()  # 允许事件循环嵌套

    asyncio.run(DouyinHotTopicSpiderWeb.main_spider())
