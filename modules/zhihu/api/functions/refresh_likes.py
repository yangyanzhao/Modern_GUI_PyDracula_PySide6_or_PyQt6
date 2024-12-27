"""
刷赞-控制器
"""
import asyncio
import datetime
import json
import logging
import os
import random
import re
import subprocess
import traceback
from asyncio import Lock

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


class RefreshLikes:
    task_type = 14

    def __init__(self, pool, html_lock: Lock, command: str, account_username: str, account_name: str,
                 user_data_dir_path: str,
                 remote_debugging_port: int, browser_type: str, home_urls: list[str], hide: bool = False):
        self.pool = pool
        self.html_lock = html_lock
        self.resourcesService = None  # 需要用到数据库，只能异步初始化，无法在同步的init中。
        self.url = "https://www.zhihu.com/creator/featured-question/recommend"
        self.type = "RefreshLikes"
        self.command = command
        if hide:
            self.command = command + " --window-position=10000,10000 "
        self.account_username = account_username
        self.account_name = account_name
        self.user_data_dir_path = user_data_dir_path
        self.remote_debugging_port = remote_debugging_port
        self.browser_type = browser_type
        self.home_urls: list[str] = home_urls

    async def run(self):
        # 进行循环，但是要排除自己
        r = []
        for home_url in self.home_urls:
            result: dict = await self.run_single_answer(home_url=home_url)
            r.append(result)
        return {"code": True, "message": f"顺利走完流程:{json.dumps(r)}"}

    async def run_single_answer(self, home_url, zan=True, comment=False, share=False, collect=False, like=False):
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
                # 按ESC键退出升级页面
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")
                logging.info(f"导航到URL: {self.url}")
                await self.page.goto(url=home_url + "/answers", timeout=60 * 1000)
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
                await asyncio.sleep(3)

                logging.info("获取列表")
                file_input_selector = 'xpath=//div[@class="List Profile-answers" and @id="Profile-answers"]//div[@class="List-item" and @tabindex="0"]'
                selector_all = await self.page.query_selector_all(file_input_selector)

                def get_one_selector(selector_list):
                    """
                    获取一条进行阅读
                    """
                    if len(selector_list) == 0:
                        return
                    selector_random = selector_list[0]
                    button_judge_1 = selector_random.query_selector('.Button:has-text("已赞同")')
                    button_judge_2 = selector_random.query_selector('.Button:has-text("取消喜欢")')
                    # 如果存在已赞同或者取消喜欢按钮，则说明已经看过了
                    if button_judge_1 is not None or button_judge_2 is not None:
                        # 删除这一条
                        del selector_list[0]
                        return get_one_selector(selector_list)
                    else:
                        return selector_list[0]

                logging.info("一直拿到没有看过的一条")
                selector_one = get_one_selector(selector_all)
                if selector_one is None:
                    logging.info("全都看过了,结束任务")
                    return {"code": False, "message": "全都看过了,结束任务"}
                title_selector = await selector_one.query_selector('xpath=//h2[@class="ContentItem-title"]')
                complete_title = await title_selector.text_content()
                logging.info("阅读全文")
                button_read_all = await selector_one.query_selector('text="阅读全文"')
                await button_read_all.click()
                randint = random.randint(30, 60)
                logging.info(f"阅读一会:{randint}秒")
                await asyncio.sleep(randint)
                selector = await selector_one.query_selector('.RichContent-inner')
                complete_content = await selector.text_content()
                exclude_selectors = await selector_one.query_selector_all('.RichText-LinkCardContainer')
                if exclude_selectors is not None and len(exclude_selectors) > 0:
                    for e in exclude_selectors:
                        ex_content = await e.text_content()
                        if ex_content is not None and ex_content.strip() != "":
                            complete_content = complete_content.replace(ex_content, "")

                span_locator = await self.page.query_selector('.RichContent-collapsedText')
                try:
                    # 没收起来也无所谓
                    if span_locator:
                        logging.info("收起")
                        await span_locator.click()
                        await asyncio.sleep(3)
                except:
                    pass
                pass
                button_comment_link = await self.page.query_selector(
                    'xpath=//button[@type="button" and contains(text(), "条评论")]')
                if button_comment_link is None:
                    button_comment_link = await  self.page.query_selector(
                        'xpath=//button[@type="button" and contains(text(), "添加评论")]')
                if comment:
                    logging.info("进入评论区")
                    if button_comment_link is not None:
                        await button_comment_link.click()
                        await asyncio.sleep(3)
                        await self.page.wait_for_load_state()
                        logging.info("对别人的评论的评论进行评论或点击喜欢")
                        divs_locator = await self.page.query_selector_all(
                            'xpath=//div[string-length(@data-id) = 11 and translate(@data-id, "0123456789", "") = ""]')  # 这里通过data-id来获取评论，很多是父子关系的评论都扫成同级了，导致无法准确定位按钮

                        if len(divs_locator) > 2 and random.choice([True, True, False, False]):
                            logging.info("如果评论的数量大于2，则随机选择一个进行评论或点击喜欢")
                            random_choice = random.choice([i for i in range(len(divs_locator))])
                            choice_locator = divs_locator[random_choice]
                            # 获取元素下所有按钮
                            buttons_all = await choice_locator.query_selector_all('xpath=//button[@type="button"]')
                            # 获取元素下所有干扰按钮
                            buttons_Interference = await choice_locator.query_selector_all(
                                'xpath=//div[string-length(@data-id) = 11 and translate(@data-id, "0123456789", "") = ""]//button[@type="button"]')
                            interference_point = [(await b.bounding_box()['x'], await b.bounding_box()['y']) for b in
                                                  buttons_Interference]
                            # 真正元素下的按钮
                            buttons = []
                            for button in buttons_all:
                                # 对比每个按钮的坐标点位置来判断
                                # 获取元素的边界信息
                                element_box = await button.bounding_box()
                                x = element_box['x']
                                y = element_box['y']
                                if (x, y) not in interference_point:
                                    buttons.append(button)
                                pass
                            # 这里可能是两个按钮，也可能是三个按钮，第一个是“回复”，第二个是“喜欢”的数量，第三个是“查看全部XX条回复”
                            return_btn = buttons[0]
                            like_btn = buttons[1]
                            content = await return_btn.text_content()
                            if re.sub(r'\u200B', '', content) == ("回复"):
                                # 这里用endswith判断是否是回复按钮
                                await return_btn.click()
                                await asyncio.sleep(3)
                                # 提取评论内容
                                CommentContent_selector = await choice_locator.query_selector(
                                    'xpath=//div[@class="CommentContent css-1jpzztt"]')

                                commentContent = await CommentContent_selector.text_content()
                                question = f"标题是：'{complete_content}'。评论是：'{commentContent}'。"

                                prompt = ZhihuPrompt().get_comment_prompt(self.account_name)
                                logging.info(f"标题是：{complete_content}")
                                logging.info(f"评论是：{commentContent}")
                                logging.info("请求GPT")
                                result, m = await chat(self.pool, prompt, question)
                                logging.info(f"【{m}】回答：{result}")
                                if result is None or len(
                                        result) > 70 or "评论" in result or "文章" in result or "内容" in result or "标题" in result or "由于信息有限" in result or "您的提问" in result:
                                    result = ZhihuPrompt.get_text_emoticon()
                                # 有时候回答末尾的emoji识别不出来，要去掉
                                if result[-8:].startswith("&#"):
                                    result = result[:-8]
                                if result[-9:].startswith("&#"):
                                    result = result[:-9]
                                if result.startswith("评论"):
                                    result = result[3:]
                                # 有时候问题内容会影响Prompt
                                if "标题是：" in result and "内容是：" in result:
                                    result = ZhihuPrompt.get_text_emoticon()
                                # 有时候内容会带有图片
                                cleaned_text = re.sub(r'!?\[.*?\]\([^)]+\)', '', result)
                                result = cleaned_text.replace("\n", "").strip()
                                data = {
                                    'account_name': self.account_name,
                                    'model': m,
                                    'prompt': prompt,
                                    'question': question,
                                    'answer': result,
                                    'status': 1,
                                    'date': datetime.date.today(),
                                    'datetime': datetime.datetime.now(),
                                }
                                await insert(pool=self.pool, table_name='chat_history', data=data)

                                logging.info("定位富文本编辑器")
                                contenteditable_selector = 'div[contenteditable="true"]'
                                contenteditable_selector = await choice_locator.query_selector(
                                    contenteditable_selector)
                                await contenteditable_selector.focus()
                                logging.info("输入评论")
                                await self.page.keyboard.type(result, delay=100)
                                await asyncio.sleep(3)
                                button_publish = await choice_locator.query_selector(
                                    'xpath=//button[text()="发布"]')
                                if button_publish:
                                    logging.info("发布评论")
                                    await button_publish.click()
                                    await asyncio.sleep(3)
                                    await self.page.wait_for_load_state()
                                else:
                                    pass
                            text_content = await like_btn.text_content()
                            if re.sub(r'\u200B', '', text_content).isdigit():
                                # 如果是纯数字，则是like按钮
                                if random.choice([True, False]):
                                    try:
                                        logging.info("点击喜欢按钮")
                                        await like_btn.click()
                                    except:
                                        logging.info("点不到也不所谓")

                        #
                        # 定位富文本编辑器
                        logging.info("对回答文章进行评论")
                        contenteditable_selector = 'div[contenteditable="true"]'
                        query_selectors = await self.page.query_selector_all(contenteditable_selector)
                        # 聚焦编辑器
                        if len(query_selectors) > 0:

                            await query_selectors[0].focus()

                            question = f"标题是：'{complete_title}'。内容是：'{complete_content}'。请对这篇内容进行评论，回答内容不要重复我的问题，也不要出现“评论”两个字，直接给我评论的内容即可，要求评论长度不要超过20个字"
                            prompt = ZhihuPrompt().get_comment_prompt(self.account_name)
                            logging.info(f"标题是：{complete_title}")
                            logging.info(f"内容是：{complete_content}")
                            logging.info("请求GPT")
                            result, m = await chat(self.pool, prompt, question)
                            logging.info(f"【{m}】回答：{result}")
                            if result is None or len(
                                    result) > 70 or "评论" in result or "文章" in result or "内容" in result or "标题" in result or "由于信息有限" in result or "您的提问" in result:
                                result = ZhihuPrompt.get_text_emoticon()
                            # 有时候回答末尾的emoji识别不出来，要去掉
                            if result[-8:].startswith("&#"):
                                result = result[:-8]
                            if result[-9:].startswith("&#"):
                                result = result[:-9]
                            if result.startswith("评论"):
                                result = result[3:]
                            # 有时候问题内容会影响Prompt
                            if "标题是" in result and "内容是" in result:
                                result = ZhihuPrompt.get_text_emoticon()
                            # 有时候内容会带有图片
                            cleaned_text = re.sub(r'!?\[.*?\]\([^)]+\)', '', result)
                            result = cleaned_text.replace("\n", "").strip()
                            data = {
                                'account_name': self.account_name,
                                'model': m,
                                'prompt': prompt,
                                'question': question,
                                'answer': result,
                                'status': 1,
                                'date': datetime.date.today(),
                                'datetime': datetime.datetime.now(),
                            }
                            await insert(pool=self.pool, table_name='chat_history', data=data)
                            logging.info("输入评论")
                            await self.page.keyboard.type(result, delay=100)
                            # 发布评论
                            button_publish = await self.page.query_selector('xpath=//button[text()="发布"]')
                            if button_publish is not None:
                                logging.info("发布评论")
                                await button_publish.click()
                                await asyncio.sleep(3)
                                await self.page.keyboard.press("Escape")

                            button_comment_link_pick_up = await self.page.query_selector(
                                'xpath=//button[@type="button" and contains(text(), "收起评论")]')
                            if button_comment_link_pick_up is not None:
                                logging.info("收起评论")
                                await button_comment_link_pick_up.click()
                                await asyncio.sleep(3)
                            else:
                                logging.info("评论界面是弹窗，按ESC键关闭")
                                await self.page.keyboard.press("Escape")
                                await self.page.keyboard.press("Escape")
                                await self.page.keyboard.press("Escape")
                                await self.page.keyboard.press("Escape")
                                await self.page.keyboard.press("Escape")
                                await asyncio.sleep(3)
                # 按ESC键退出升级页面
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")
                # 点击喜欢
                if like:
                    logging.info("进入喜欢区")
                    button_like = selector_one.query_selector('.Button:has-text("喜欢")')
                    await self.page.keyboard.press("Escape")
                    if button_like is not None:
                        await self.page.keyboard.press("Escape")
                        try:
                            logging.info("点击喜欢")
                            button_like.click()
                        except:
                            # 有时候遮罩Esc去不掉，就会发生这种错误
                            await self.page.keyboard.press("Escape")
                            await self.page.keyboard.press("Escape")
                            await self.page.keyboard.press("Escape")
                            pass
                        await asyncio.sleep(3)
                # 点击赞同
                if zan:
                    try:
                        logging.info("进入赞同区")
                        button_agree = selector_one.query_selector('.Button:has-text("赞同")')
                        if button_agree is not None:
                            logging.info("点击赞同")
                            button_agree.click()
                            await asyncio.sleep(3)
                    except:
                        pass
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")
                await self.page.keyboard.press("Escape")
                if share:
                    # 点击分享
                    logging.info("进入分享区")
                    button_share = selector_one.query_selector('.Button:has-text("分享")')
                    if button_share is not None:
                        button_share.click()
                        await asyncio.sleep(3)
                        # 复制链接
                        button_share_link = await self.page.query_selector(
                            'xpath=//button[@class="Button Menu-item ShareMenu-button Button--plain" and contains(text(), "复制链接")]')
                        if button_share_link is not None:
                            logging.info("点击分享")
                            await button_share_link.click()
                            await asyncio.sleep(3)
                if collect:
                    # 点击收藏
                    logging.info("进入收藏区")
                    button_collection = selector_one.query_selector('.Button:has-text("收藏")')
                    if button_collection is not None:
                        button_collection.click()
                        await asyncio.sleep(3)
                        logging.info("选择收藏夹")
                        selection = await self.page.query_selector_all(
                            'xpath=//button[@class="Button Favlists-updateButton Button--blue" and text()="收藏"]')
                        if selection is not None and len(selection) > 0:
                            await selection[0].click()
                            await asyncio.sleep(2)
                            # 关闭弹窗
                            await self.page.keyboard.press("Escape")
                            await self.page.keyboard.press("Escape")
                            await self.page.keyboard.press("Escape")
                        else:
                            logging.info("创建一个收藏夹")
                            button_create_collection = await self.page.query_selector(
                                'xpath=//button[text()="创建收藏夹"]')
                            # 点击按钮
                            await button_create_collection.click()
                            await asyncio.sleep(3)
                            # 输入收藏标题
                            # 使用 XPath 选择器定位 input
                            xpath_input = '//input[@placeholder="收藏标题"]'
                            # 等待 input 元素出现在页面上
                            await self.page.wait_for_selector(xpath_input)
                            # 聚焦 input 元素
                            await self.page.focus(xpath_input)
                            # 输入文字
                            await self.page.keyboard.type(f"我的收藏{datetime.date.today()}{random.randint(0, 99)}",
                                                          delay=100)
                            await asyncio.sleep(3)

                            # 输入收藏描述
                            # 使用 XPath 选择器定位 textarea
                            textarea_xpath_selector = '//textarea[@placeholder="收藏描述（可选）"]'
                            # 等待 textarea 元素出现在页面上
                            await self.page.wait_for_selector(textarea_xpath_selector)
                            # 聚焦 textarea 元素
                            await self.page.focus(textarea_xpath_selector)
                            # 输入文字
                            await self.page.keyboard.type(f"我的收藏{random.randint(100, 9999)}", delay=100)
                            await asyncio.sleep(3)
                            # 确定创建
                            submit = await self.page.query_selector(
                                'xpath=//button[@type="submit" and text()="确认创建"]')
                            # 执行操作，例如点击（如果需要的话，尽管按钮是禁用状态）
                            logging.info("点击确定创建收藏夹")
                            await submit.click()
                            await asyncio.sleep(3)
                        # 按ESC键退出升级页面
                        await self.page.keyboard.press("Escape")
                        await self.page.keyboard.press("Escape")
                        await self.page.keyboard.press("Escape")
                        await asyncio.sleep(3)
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
    file_handler = logging.FileHandler(filename=os.path.join(logs_dir, f'refresh_likes_{datetime.date.today()}.log'),
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
            recommend = RefreshLikes(pool=pool, html_lock=html_lock, command=find['command'],
                                     account_username=account['username'],
                                     account_name=account['account_name'],
                                     remote_debugging_port=account['remote_debugging_port'],
                                     browser_type=account['browser_type'], home_urls=[], hide=False)
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
            await close_pool(pool)


    while True:
        asyncio.run(start())
