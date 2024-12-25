"""
关注(右侧推荐栏)-控制器
2024年9月22日21:30:18 调试通过
"""
import asyncio
import datetime
import logging
import os
import subprocess
import traceback
from asyncio import Lock

from playwright.async_api import async_playwright

from modules.zhihu_auto.api.resource.resources_service import ResourcesService
from modules.zhihu_auto.api.utils.common_utils import close_browser_by_domain, kill_process_by_port, \
    kill_processes_by_user_data_dir, ping_website
from db.mysql.mysql_jdbc import insert, select_list, create_pool
from modules.zhihu_auto.plugin_email.email_notice import email_notification
from modules.zhihu_auto.plugin_screenshot.screenshot_page_element import screenshot_page

from modules.zhihu_auto.api.functions import current_directory

util_html_path = os.path.join(current_directory, "html_utils", "util.html")
markdown_html_path = os.path.join(current_directory, "html_utils", "markdown.html")


class FollowRecommend:
    task_type = 13

    def __init__(self, pool, html_lock: Lock, command: str, account_username: str, account_name: str,
                 user_data_dir_path: str,
                 remote_debugging_port: int, browser_type: str, hide: bool = False, mock_text=None):
        self.pool = pool
        self.html_lock = html_lock
        self.resourcesService = None  # 需要用到数据库，只能异步初始化，无法在同步的init中。
        self.type = "FollowRecommend"
        self.command = command
        if hide:
            self.command = command + " --window-position=10000,10000 "
        self.url = "https://www.zhihu.com/"
        self.account_username = account_username
        self.account_name = account_name
        self.user_data_dir_path = user_data_dir_path
        self.remote_debugging_port = remote_debugging_port
        self.browser_type = browser_type
        self.mock_text = mock_text  # 这个是用来调试用的，如果输入模拟答案，则不会去向GPT聊天，而是直接返回模拟的答案。

    async def run(self):
        # 清理页面
        logging.info("开始清理页面")
        await close_browser_by_domain(self)
        # 清理端口占用
        logging.info(f"开始清理端口占用，端口: {self.remote_debugging_port}")
        await kill_process_by_port(self.remote_debugging_port)
        logging.info(f"开始清理，用户数据目录: {self.user_data_dir_path}")
        await kill_processes_by_user_data_dir(self.user_data_dir_path)
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
                return {"code": False, "message": "Chrome进程启动失败"}
            async with async_playwright() as p:
                # 创建一个连接
                logging.info(f"连接到Chrome，端口: {self.remote_debugging_port}")
                self.browser = await  p.chromium.connect_over_cdp(f"http://localhost:{self.remote_debugging_port}")
                self.content = self.browser.contexts[0]
                self.page = await self.content.new_page()
                # 按ESC键退出升级页面
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")
                logging.info("这里ping一下网络通不通")
                if not ping_website("www.zhihu.com"):
                    logging.info("网络不通")
                    return {"code": False, "message": "网络不通"}
                logging.info(f"导航到URL: {self.url}")
                await self.page.goto(self.url, timeout=60 * 1000)
                await self.page.wait_for_load_state('networkidle')
                # 按ESC键退出升级页面
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")
                # 监测一下是不是登录页面，如果是登录页面，则在页面上标记账号，并定期循环监测，直到登录成功。
                count = 0
                while True:
                    await asyncio.sleep(1)
                    logging.info(f"请登录:{datetime.datetime.now()}")
                    if self.page.url.startswith('https://www.zhihu.com/signin'):
                        if await self.page.locator('input[placeholder="手机号"]').is_visible():
                            value = await self.page.locator('input[placeholder="手机号"]').input_value()
                            if value != self.account_name:
                                await self.page.locator('input[placeholder="手机号"]').fill(self.account_name)
                            pass
                            if count % 10 == 0:
                                logging.info("账号信息不正确，请检查账号信息是否正确")
                                # 进行截图发邮件，这样可以远程扫码登录。
                                page_path = await screenshot_page(page=self.page,
                                                                  file_name=datetime.datetime.now().strftime(
                                                                      '%Y-%m-%d_%H-%M-%S-%f'))
                                # 发送邮件
                                await email_notification(message=f"请扫码登录，账号:{self.account_username}",
                                                         image_paths=[page_path])
                            count += 1
                            continue
                        else:
                            break
                    else:
                        break
                await asyncio.sleep(1)
                logging.info("登录成功！")
                await self.page.wait_for_load_state('networkidle')
                # 按ESC键退出升级页面
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")
                # 检查包含特定文本的元素是否存在
                while True:
                    element_upgrade = await self.page.query_selector_all('text="系统升级中，请稍后再试"')
                    if len(element_upgrade) > 0:
                        await asyncio.sleep(10)
                        # 等待10秒，刷新页面
                        await self.page.reload()
                    else:
                        break
                logging.info("定位到推荐横杠栏")
                selector_all = await self.page.query_selector_all(
                    'div[itemprop="author"][itemtype="http://schema.org/Person"].AuthorInfo')
                if len(selector_all) == 0:
                    return {"code": False, "message": "未找到任何推荐的知友"}
                for index, selector in enumerate(selector_all[:4]):
                    pass
                    logging.info("定位用户名称")
                    user_name_element = await selector.query_selector(
                        'xpath=//span[@class="UserLink AuthorInfo-name"]//a')
                    username = await user_name_element.text_content()
                    logging.info("定位推荐理由")
                    recommend_reason_element = await selector.query_selector('xpath=//div[@class="AuthorInfo-badge"]')
                    recommend_reason = await recommend_reason_element.text_content()
                    # 定位同级别按钮
                    # 先定位父元素
                    parent_element = await selector.query_selector('xpath=..')
                    logging.info("在定位旗下的按钮元素")
                    another_button_selector = 'button[type="button"].Button.FollowButton:has-text("关注")'
                    await self.page.wait_for_selector(another_button_selector, timeout=60 * 1000)
                    another_button = await parent_element.query_selector(another_button_selector)
                    if another_button is not None:
                        logging.info(f"点击关注:{index}")
                        await another_button.click()

                        data = {
                            'account_name': self.account_name,
                            'type': self.type,
                            'name': username,
                            'recommend_reason': recommend_reason,
                            'status': 1,
                            'date': datetime.date.today(),
                            'datetime': datetime.datetime.now()
                        }
                        await insert(pool=self.pool, table_name='follow', data=data)
                    else:
                        print(f"")
                        logging.info(f"another_button为None，无法点击！！:{index}")
                return {"code": True, "message": "顺利走完流程"}
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            traceback.print_exc()
            exc_info = traceback.format_exc()
            logging.error(exc_info)
            return {"code": False, "message": f"{exc_info}"}
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
                logging.info(f"开始清理，用户数据目录: {self.user_data_dir_path}")
                await kill_processes_by_user_data_dir(self.user_data_dir_path)
            except Exception as e:
                logging.error(f"Failed to clean up resources: {e}")


if __name__ == '__main__':
    import nest_asyncio

    # 创建日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logs_dir = fr'logs\{datetime.date.today()}'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    # 创建文件处理器，将日志写入文件
    file_handler = logging.FileHandler(filename=os.path.join(logs_dir, f'follow_recommend_{datetime.date.today()}.log'),
                                       mode='a',
                                       encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    # 创建控制台处理器，将日志输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    # 将处理器添加到日志记录器
    logger.addHandler(file_handler)

    nest_asyncio.apply()  # 允许事件循环嵌套


    async def run_task(pool, html_lock, resource_lock, account, accounts):
        find_list = await select_list(pool=pool, table_name="task_plan",
                                      condition={"account_id": account["id"], 'task_type': 1, 'status': 1},
                                      order_by=["priority"], order_direction=["desc"])
        if len(find_list) > 0:
            find = find_list[0]
            recommend = FollowRecommend(pool=pool, html_lock=html_lock, command=find['command'],
                                        account_username=account['username'],
                                        account_name=account['account_name'],
                                        remote_debugging_port=account['remote_debugging_port'],
                                        browser_type=account['browser_type'], hide=True)
            # 初始化资源管理器
            recommend.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock, accounts=accounts)
            await recommend.run()


    async def start():
        # 在当前loop中创建一个异步锁
        html_lock: Lock = asyncio.Lock()
        resource_lock: Lock = asyncio.Lock()
        # 创建数据库连接池
        pool = await create_pool(db='zhihu')
        try:
            accounts = await select_list(pool=pool, table_name="account", condition={"status": 1})
            # 创建任务组
            async with asyncio.TaskGroup() as tg:
                for account in accounts:
                    tg.create_task(run_task(pool, html_lock, resource_lock, account, accounts))
        finally:
            pool.close()  # 手动关闭连接
            await pool.wait_closed()  # 等待连接关闭


    asyncio.run(start())
