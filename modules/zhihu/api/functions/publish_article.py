"""
发布文章-控制器
2024年9月13日22:56:40 调试通过
"""
import asyncio
import datetime
import logging
import os
import random
import re
import time
import subprocess
import traceback
from asyncio import Lock

import pyperclip
from playwright.async_api import async_playwright
from modules.zhihu.api.resource.resources_service import ResourcesService
from modules.zhihu.api.utils.common_utils import close_browser_by_domain, kill_process_by_port, \
    kill_processes_by_user_data_dir, ping_website
from db.mysql.mysql_jdbc import insert, select_list, create_pool
from modules.zhihu.plugin_email.email_notice import email_notification
from modules.zhihu.plugin_screenshot.screenshot_page_element import screenshot_page
from modules.zhihu.api.resource.zhihu_prompt import ZhihuPrompt
from modules.zhihu.chat.api import chat
from db.mysql.mysql_jdbc import insert, select_list, create_pool, close_pool


from modules.zhihu.api.functions import current_directory
util_html_path = os.path.join(current_directory, "html_utils", "util.html")
markdown_html_path = os.path.join(current_directory, "html_utils", "markdown.html")


class PublishArticle:
    task_type = 8
    task_type_草稿 = 9

    def __init__(self, pool, html_lock: Lock, command: str, account_username: str, account_name: str,user_data_dir_path:str,
                 remote_debugging_port: int, browser_type: str, draft: bool = False, hide: bool = False,
                 mock_text=None):
        self.pool = pool
        self.html_lock = html_lock
        self.resourcesService = None  # 需要用到数据库，只能异步初始化，无法在同步的init中。
        self.draft = draft
        self.type = "PublishArticle"
        self.url = "https://zhuanlan.zhihu.com/write"
        self.command = command
        if hide:
            self.command = command + " --window-position=10000,10000 "
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
                self.browser = await p.chromium.connect_over_cdp(f"http://localhost:{self.remote_debugging_port}")
                self.content = self.browser.contexts[0]
                self.page = await self.content.new_page()
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

                article_topic = "模拟话题"
                logging.info(f"获取话题:{article_topic}")
                result = None
                m = '模拟'
                prompt = None
                if self.mock_text is not None:
                    result = self.mock_text
                else:
                    logging.info(f"请求GPT")
                    article_topic = await self.resourcesService.get_hot_topic()
                    prompt = ZhihuPrompt().get_article_prompt(self.account_name, 1500)
                    result, m = await chat(self.pool, prompt, article_topic)
                    pass
                logging.info(f"【{m}】回答：{result}")

                if result is None:
                    logging.error("请求GPT失败,放弃此次发布文章")
                    return {"code": False, "message": "请求GPT失败,放弃此次发布文章"}
                logging.info(f"记录GPT回答历史")

                data = {
                    'account_name': self.account_name,
                    'model': m,
                    'prompt': prompt,
                    'question': article_topic,
                    'answer': result,
                    'status': 1,
                    'date': datetime.date.today(),
                    'datetime': datetime.datetime.now(),
                }
                await insert(pool=self.pool, table_name='chat_history', data=data)

                logging.info("使用正则表达式找到所有句号的位置")
                sentences = re.split(r'(?<=\。)\s*', result.replace("```json", "").replace("```", ""))
                logging.info("计算每段的句子数量")
                num_sentences = len(sentences)
                sentences_per_part = num_sentences // 3
                logging.info("分割文本")
                first = ' '.join(sentences[:sentences_per_part])
                second = ' '.join(sentences[sentences_per_part:2 * sentences_per_part])
                third = ' '.join(sentences[2 * sentences_per_part:])

                # 使用 XPath 选择器定位 textarea
                textarea_xpath_selector = '//textarea[@placeholder="请输入标题（最多 100 个字）"]'

                logging.info("等待 textarea 元素出现在页面上")
                await self.page.wait_for_selector(textarea_xpath_selector)

                logging.info("聚焦 textarea 元素")
                await self.page.focus(textarea_xpath_selector)

                # 输入文字
                logging.info("输入文字")
                await self.page.keyboard.type(article_topic, delay=100)

                await asyncio.sleep(3)

                logging.info("定位到富文本编辑器")
                contenteditable_selector = 'div[contenteditable="true"]'

                logging.info("等待富文本编辑器出现在页面上")
                await self.page.wait_for_selector(contenteditable_selector)

                logging.info("聚焦富文本编辑器")
                await self.page.focus(contenteditable_selector)

                logging.info("拿三张照片")

                await asyncio.sleep(0.5)
                logging.info("输入文字")
                # 采用工具页面进行复制粘贴
                # 现将文本输入
                async with self.html_lock:
                    logging.info("利用页面进行markdown格式转换")
                    page_json = await self.content.new_page()
                    logging.info(f"导航到Markdown页面: {markdown_html_path}")
                    await page_json.goto(markdown_html_path,
                                         wait_until="commit", timeout=60 * 1000)
                    # 聚焦输入框
                    await page_json.click('div[class="CodeMirror-code"]')
                    await page_json.click('div[class="CodeMirror-code"]')
                    await page_json.click('div[class="CodeMirror-code"]')

                    # page_json.keyboard.type(result)
                    pyperclip.copy(result)
                    # 全选文本
                    await page_json.keyboard.down('Control')
                    await page_json.keyboard.press('A')
                    await page_json.keyboard.up('Control')
                    await page_json.keyboard.press('Delete')
                    # 粘贴文本
                    await page_json.keyboard.down('Control')
                    await page_json.keyboard.press('V')
                    await page_json.keyboard.up('Control')

                    # 将剪切板中的数据输入到临时文件中
                    await page_json.close()
                    # 再复制到知乎文本框中
                    all_pages = self.content.pages
                    self.page = all_pages[1]

                    logging.info("定位到富文本编辑器")
                    contenteditable_selector = 'div[contenteditable="true"]'
                    logging.info("等待富文本编辑器出现在页面上")
                    await self.page.wait_for_selector(contenteditable_selector)
                    logging.info("聚焦富文本编辑器")
                    await self.page.focus(contenteditable_selector)

                    # 全选文本
                    await self.page.keyboard.down('Control')
                    await self.page.keyboard.press('A')
                    await self.page.keyboard.up('Control')
                    await self.page.keyboard.press('Delete')
                    # 粘贴文本
                    await self.page.keyboard.down('Control')
                    await self.page.keyboard.press('V')
                    await self.page.keyboard.up('Control')
                    await self.page.wait_for_load_state('networkidle')

                logging.info("获取三张图片")
                pictures = await self.resourcesService.get_three_pictures(account_username=self.account_username,
                                                                          account_name=self.account_name,
                                                                          type="PublishArticle", pic_number=3)
                await asyncio.sleep(3)

                if pictures:
                    logging.info(f"获得图片数量:{len(pictures)}")
                    button_locator = await self.page.query_selector('button[type="button"][aria-label="图片"]')
                    logging.info("点击上传图片")
                    try:
                        await button_locator.click()
                    except:
                        pass
                    await asyncio.sleep(3)

                    # 定位上传标签
                    file_input_selector = 'xpath=//input[@type="file" and @accept="image/*"]'
                    # 使用 page.set_input_files 上传文件
                    try:

                        await self.page.set_input_files(file_input_selector, pictures)
                    except:
                        traceback.print_exc()
                        exc_info = traceback.format_exc()
                        logging.error(exc_info)
                        # 截图
                        page_path = await screenshot_page(page=self.page,
                                                          file_name=datetime.datetime.now().strftime(
                                                              '%Y-%m-%d_%H-%M-%S-%f'))
                        # 发送邮件
                        await email_notification(message=f"random_browsing_289行:{exc_info}",
                                                 image_paths=[page_path])
                        # 睡三秒再试试
                        await asyncio.sleep(3)
                        await self.page.set_input_files(file_input_selector,
                                                        pictures)  # TODO 经常 ！！！ 这里会报错：Timeout 30000ms exceeded.waiting for locator("//input[@type=\"file\" and @accept=\"image/*\"]")，playwright._impl._errors.TimeoutError: Page.set_input_files: Timeout 30000ms exceeded.

                    logging.info("有的图片有点大，睡一会")
                    await asyncio.sleep(20)
                    button_locator = await self.page.query_selector('button:has-text("插入图片")')
                    await button_locator.click()
                    logging.info("插入图片，睡一会")
                    await asyncio.sleep(20)

                logging.info("鼠标往下滑动")
                await self.page.mouse.wheel(0, 2000)
                await asyncio.sleep(10)
                if pictures:
                    file_input_cover = 'xpath=//input[@type="file" and @class="UploadPicture-input"]'
                    logging.info("添加文章封面")
                    await self.page.set_input_files(file_input_cover, [pictures[0]])
                    await asyncio.sleep(10)
                try:
                    logging.info("添加文章话题")
                    button_add_topic_selector = await self.page.query_selector(
                        'button[class="css-1gtqxw0"] >> text="添加话题"')
                    # 如果系统没有自动添加话题，则点击添加话题
                    if button_add_topic_selector is not None:
                        await button_add_topic_selector.click()
                        await asyncio.sleep(3)
                        # 输入标题
                        input_xpath_selector = '//input[@placeholder="搜索话题..." and @aria-label="搜索话题"]'
                        # 等待 input 元素出现在页面上
                        await self.page.wait_for_selector(input_xpath_selector)
                        # 聚焦 input 元素
                        await self.page.focus(input_xpath_selector)
                        # 输入文字
                        await self.page.keyboard.type(article_topic, delay=100)
                        await asyncio.sleep(6)
                        # 选择话题
                        select_topic_selector = 'xpath=//div[@class="css-ogem9c"]//button[@class="css-gfrh4c"]'
                        selector_all = await self.page.query_selector_all(select_topic_selector)
                        # 随机点一个就行
                        randint = random.randint(0, len(selector_all) - 1)
                        await selector_all[randint].click()
                except:
                    pass
                data = {
                    "account_name": self.account_name,
                    "type": "PublishArticle",
                    "title": article_topic,
                    "status": 1,
                    'is_success': False,
                    "date": datetime.date.today(),
                    "datetime": datetime.datetime.now()
                }
                is_success = False
                if not self.draft:

                    # 定位发布按钮
                    button_selector = 'button[type="button"] >> text="发布"'
                    logging.info("点击发布")
                    await asyncio.sleep(10)
                    await self.page.click(button_selector)
                    logging.info("等待页面跳转事件")
                    await asyncio.sleep(3)
                    logging.info("更新 self.page 指向新的页面")
                    logging.info("获取所有打开的页面")
                    all_pages = self.page.context.pages
                    logging.info("选择最新的页面")
                    new_page = all_pages[-1]
                    logging.info("更新 self.page 指向新的页面")
                    self.page = new_page
                    # 这里要校验一下是不是发布成功
                    for i in range(10):
                        await asyncio.sleep(1)
                        # 这里要校验一下是不是发布成功
                        qs = await self.page.query_selector('button[type="button"] >> text="设置"')
                        if qs is not None:
                            await qs.click()# playwright._impl._errors.TimeoutError: ElementHandle.click: Timeout 30000ms exceeded. TODO
                            time.sleep(0.5)
                            is_success = await self.page.query_selector(
                                'button[type="button"] >> text="修改文章"') is not None
                            if is_success:
                                break
                    logging.info(f"校验是否发布成功:{is_success}")
                    data['is_success'] = is_success
                # 删除已使用图片
                await self.resourcesService.del_pictures(pictures)
                logging.info("文章存入数据库")
                await insert(pool=self.pool, table_name='publish_articles', data=data)

                await asyncio.sleep(3)
                if self.draft:
                    return {"code": True,
                            "message": "顺利走完流程"}
                else:
                    return {"code": is_success,
                            "message": "顺利走完流程" if is_success else "顺利走完流程，但是未检测到发布成功(可能是草稿)"}
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
    file_handler = logging.FileHandler(filename=os.path.join(logs_dir, f'publish_article_{datetime.date.today()}.log'),
                                       mode='a',
                                       encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    # 将处理器添加到日志记录器
    logger.addHandler(file_handler)

    nest_asyncio.apply()  # 允许事件循环嵌套


    async def run_task(pool, html_lock, resource_lock, account, accounts):
        find_list = await select_list(pool=pool, table_name="task_plan",
                                      condition={"account_id": account["id"], 'task_type': 1, 'status': 1},
                                      order_by=["priority"], order_direction=["desc"])
        if len(find_list) > 0:
            find = find_list[0]
            recommend = PublishArticle(pool=pool, html_lock=html_lock, command=find['command'],
                                       account_username=account['username'],
                                       account_name=account['account_name'],
                                       remote_debugging_port=account['remote_debugging_port'],
                                       browser_type=account['browser_type'], draft=False, hide=False)
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
                    break
        finally:
            await close_pool(pool)


    while True:
        asyncio.run(start())
