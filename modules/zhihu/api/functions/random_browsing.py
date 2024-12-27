"""
漫游控制器
2024年9月22日21:30:26 调试通过
"""
import asyncio
import datetime
import logging
import os
import random
import re
import subprocess
import time
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


class RandomBrowsing:
    """
    随机漫游
    """
    task_type = 15

    def __init__(self, pool, html_lock: Lock, command: str, account_username: str, account_name: str,user_data_dir_path:str,
                 remote_debugging_port: int, browser_type: str, duration=60 * 10, hide: bool = False, mock_text=None):
        self.pool = pool
        self.html_lock = html_lock
        self.resourcesService = None  # 需要用到数据库，只能异步初始化，无法在同步的init中。
        self.type = "RandomBrowsing"
        self.command = command
        if hide:
            self.command = command + " --window-position=10000,10000 "
        self.url = "https://www.zhihu.com"
        self.account_username = account_username
        self.account_name = account_name
        self.user_data_dir_path = user_data_dir_path
        self.remote_debugging_port = remote_debugging_port
        self.browser_type = browser_type
        self.duration = duration
        self.mock_text = mock_text  # 这个是用来调试用的，如果输入模拟答案，则不会去向GPT聊天，而是直接返回模拟的答案。

    async def run(self):
        # 计算出结束时间
        end_time = time.time() + self.duration
        logging.info(f"开始随机浏览，将持续{self.duration}秒【{self.duration / 60}分钟】")

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
                await asyncio.sleep(3)
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

                logging.info("点击推荐")
                link_locator = await self.page.query_selector('.TopstoryTabs-link:has-text("推荐")')
                if link_locator:
                    await link_locator.click()
                else:
                    logging.info("链接未找到")
                while time.time() < end_time:
                    # 按ESC键退出升级页面
                    await self.page.keyboard.press("Escape")
                    await self.page.keyboard.press("Escape")
                    await self.page.keyboard.press("Escape")
                    randint = random.randint(30, 60)
                    logging.info(f"随机停顿 {randint} 秒")
                    await asyncio.sleep(randint)

                    logging.info(f"获取浏览列表")
                    file_input_selector = 'xpath=//div[@class="Topstory-recommend" and @data-zop-feedlistfather="0"]//div[@class="Card TopstoryItem TopstoryItem-isRecommend" and @tabindex="0"]'
                    selector_all = await self.page.query_selector_all(file_input_selector)
                    logging.info(f"获取一条进行阅读")

                    async def get_one_selector(selector_list):
                        """
                        递归获取一条进行阅读
                        """
                        if len(selector_list) == 0:
                            return
                        selector_random = selector_list[0]
                        button_judge_1 = await selector_random.query_selector('.Button:has-text("已赞同")')
                        button_judge_2 = await selector_random.query_selector('.Button:has-text("取消喜欢")')
                        # 如果存在已赞同或者取消喜欢按钮，则说明已经看过了
                        if button_judge_1 is not None or button_judge_2 is not None:
                            # 删除这一条
                            del selector_list[0]
                            return await get_one_selector(selector_list)
                        else:
                            return selector_list[0]

                    # 一直拿到没有看过的一条
                    selector_one = await get_one_selector(selector_all)
                    if selector_one is None:
                        # 说明全都看过了
                        logging.info(f"全都看过了，一条没获取到")
                        continue

                    title_selector = await selector_one.query_selector('xpath=//h2[@class="ContentItem-title"]')
                    complete_title = await title_selector.text_content()
                    logging.info(f"获取标题:{complete_title}")

                    button_read_all = await selector_one.query_selector('text="阅读全文"')
                    logging.info(f"点击阅读全文")
                    await button_read_all.click()
                    # 阅读一会
                    random_randint = random.randint(10, 60)
                    logging.info(f"阅读一会 {random_randint} 秒")
                    await asyncio.sleep(random_randint)

                    selector = await selector_one.query_selector('.RichContent-inner')
                    logging.info(f"获取内容")
                    complete_content = await selector.text_content()
                    exclude_selectors = await selector_one.query_selector_all('.RichText-LinkCardContainer')
                    if exclude_selectors is not None and len(exclude_selectors) > 0:
                        for e in exclude_selectors:
                            ex_content = await e.text_content()
                            if ex_content is not None and ex_content.strip() != "":
                                complete_content = complete_content.replace(ex_content, "")
                    logging.info(f"内容:{complete_content}")
                    try:
                        logging.info(f"尝试收起全文")
                        span_locator = await self.page.query_selector('.RichContent-collapsedText')
                        if span_locator:
                            await span_locator.click()
                            await asyncio.sleep(3)
                    except:
                        pass
                    pass

                    def generate_values():
                        # 赞同和喜欢至少有一个是True
                        agree = random.choice([True, False])
                        like = random.choice([True, False])
                        share = random.choice([True, False, False, False])
                        collection = random.choice([True, False, False, False])
                        comment = random.choice([True, True, True, False, False])
                        refresh = False
                        if not agree and not like:
                            refresh = True
                        return agree, like, share, collection, comment, refresh
                        # return True, True, True, True, True, True

                    pass
                    # 点赞、喜欢、分享、收藏、评论、刷新
                    agree, like, share, collection, comment, refresh = generate_values()
                    logging.info({"赞同": agree, "喜欢": like, "分享": share, "收藏": collection, "评论": comment,
                                  "刷新": refresh})
                    if comment:
                        logging.info(f"走入评论区")
                        button_comment_link = await self.page.query_selector(
                            'xpath=//button[@type="button" and contains(text(), "条评论")]')
                        if button_comment_link is not None:
                            await button_comment_link.click()
                            await asyncio.sleep(3)
                            await self.page.wait_for_load_state()
                            logging.info("对别人的评论的评论进行评论或点击喜欢")
                            divs_locator = await self.page.query_selector_all(
                                'xpath=//div[string-length(@data-id) = 11 and translate(@data-id, "0123456789", "") = ""]')  # 这里通过data-id来获取评论，很多是父子关系的评论都扫成同级了，导致无法准确定位按钮

                            if len(divs_locator) > 2 and random.choice([True, True, True, False]):
                                logging.info("如果评论的数量大于2，则随机选择一个进行评论或点击喜欢")
                                random_choice = random.choice([i for i in range(len(divs_locator))])
                                choice_locator = divs_locator[random_choice]
                                # 获取元素下所有按钮
                                buttons_all = await choice_locator.query_selector_all('xpath=//button[@type="button"]')
                                # 获取元素下所有干扰按钮
                                buttons_Interference = await choice_locator.query_selector_all(
                                    'xpath=//div[string-length(@data-id) = 11 and translate(@data-id, "0123456789", "") = ""]//button[@type="button"]')

                                interference_point = []
                                for b in buttons_Interference:
                                    box = await b.bounding_box()
                                    x = box['x']
                                    y = box['y']
                                    interference_point.append((x, y))

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
                                try:
                                    like_btn = buttons[1]  # 这里可能报错：IndexError: list index out of range TODO
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
                                # 这里还要做一层判断，判断一下是不是：付费阅读内容仅会员可评论
                                div_vip_selector = await selector_one.query_selector(
                                    'div:has-text("付费阅读内容仅会员可评论")')
                                if re.sub(r'\u200B', '', await return_btn.text_content()) == ("回复") and div_vip_selector is None:
                                    # 这里用endswith判断是否是回复按钮
                                    await return_btn.click()
                                    await asyncio.sleep(3)
                                    # 提取评论内容
                                    CommentContent_selector = await choice_locator.query_selector(
                                        'xpath=//div[@class="CommentContent css-1jpzztt"]')
                                    commentContent = await CommentContent_selector.text_content()

                                    question = f"标题是：'{complete_content.encode('utf-8').decode('utf-8')}'。评论是：'{commentContent.encode('utf-8').decode('utf-8')}'。"
                                    logging.info(f"标题:{complete_content}")
                                    logging.info(f"评论:{commentContent}")
                                    logging.info(f"请求GPT，请耐心等待...")
                                    prompt = ZhihuPrompt().get_comment_prompt(self.account_name)
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
                                    result = cleaned_text.replace("\n", "").strip().encode('utf-8').decode('utf-8')
                                    logging.info("记录GPT请求历史")

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

                                    logging.info(f"定位富文本编辑器")
                                    contenteditable_selector = 'div[contenteditable="true"]'
                                    contenteditable_selector = await choice_locator.query_selector(
                                        contenteditable_selector)
                                    await asyncio.sleep(3)
                                    await contenteditable_selector.focus()
                                    await self.page.keyboard.type(result, delay=100)
                                    await asyncio.sleep(3)
                                    logging.info(f"点击发布评论")
                                    button_publish = await  choice_locator.query_selector(
                                        'xpath=//button[text()="发布"]')
                                    await button_publish.click()

                                if re.sub(r'\u200B', '', await like_btn.text_content()).isdigit():
                                    # 如果是纯数字，则是like按钮
                                    if random.choice([True, False]):
                                        try:
                                            await like_btn.click()
                                        except:
                                            # 点不到也不所谓
                                            pass

                            # 进行评论
                            logging.info("对回答进行评论或点击喜欢")
                            # 这里还要做一层判断，判断一下是不是：付费阅读内容仅会员可评论
                            div_vip_selector = await selector_one.query_selector(
                                'div:has-text("付费阅读内容仅会员可评论")')
                            # 定位富文本编辑器
                            contenteditable_selector = 'div[contenteditable="true"]'
                            query_selectors = await selector_one.query_selector_all(contenteditable_selector)
                            if len(query_selectors) > 0  and div_vip_selector is None:
                                question = f"标题是：'{complete_title}'。内容是：'{complete_content}'。请对这篇内容进行评论，回答内容不要重复我的问题，也不要出现“评论”两个字，直接给我评论的内容即可，要求评论长度不要超过20个字"
                                logging.info("请求GPT")
                                prompt = ZhihuPrompt().get_comment_prompt(self.account_name)
                                result, m = await chat(self.pool, prompt, question)
                                logging.info(f"标题是：{complete_title}")
                                logging.info(f"内容是：{complete_content}")
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
                                logging.info("记录GPT请求历史")
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

                                # 聚焦编辑器
                                try:
                                    await query_selectors[0].focus()
                                except Exception as e:
                                    logging.error(f"An error occurred: {e}")
                                    traceback.print_exc()
                                    exc_info = traceback.format_exc()
                                    logging.error(exc_info)
                                    pass
                                await self.page.keyboard.type(result, delay=100)
                                logging.info("发布评论")
                                button_publish = await self.page.query_selector('xpath=//button[text()="发布"]')
                                try:
                                    await button_publish.click()
                                except Exception as e:
                                    logging.error(f"An error occurred: {e}")
                                    traceback.print_exc()
                                    exc_info = traceback.format_exc()
                                    logging.error(exc_info)
                                    pass

                                await asyncio.sleep(3)
                                await self.page.keyboard.press("Escape")

                                button_comment_link_pick_up = await self.page.query_selector(
                                    'xpath=//button[@type="button" and contains(text(), "收起评论")]')
                                logging.info("收起评论")
                                if button_comment_link_pick_up is not None:
                                    await button_comment_link_pick_up.click()
                                    await asyncio.sleep(3)
                                else:
                                    # 评论界面是弹窗，按ESC键关闭
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

                    logging.info("进入喜欢区")
                    button_like = await selector_one.query_selector('.Button:has-text("喜欢")')
                    await self.page.keyboard.press("Escape")
                    if button_like is not None:
                        await self.page.keyboard.press("Escape")
                        if like:
                            try:
                                logging.info("点击喜欢")
                                await button_like.click()
                            except:
                                # 有时候遮罩Esc去不掉，就会发生这种错误
                                await self.page.keyboard.press("Escape")
                                await self.page.keyboard.press("Escape")
                                await self.page.keyboard.press("Escape")
                                pass
                            await asyncio.sleep(3)
                    else:
                        logging.info("如果没有喜欢按钮，则一定要点击赞同")
                        agree = True
                    try:
                        query_selector_close_btn = await self.page.query_selector(
                            'xpath=//button[@type="button" and @aria-label="关闭"]')
                        if query_selector_close_btn is not None:
                            await query_selector_close_btn.click()
                    except:
                        pass
                    # 按ESC键退出升级页面
                    await self.page.keyboard.press("Escape")
                    await self.page.keyboard.press("Escape")
                    await self.page.keyboard.press("Escape")
                    try:
                        logging.info("进入赞同区")
                        button_agree = await selector_one.query_selector('.Button:has-text("赞同")')
                        if button_agree is not None:
                            if agree:
                                logging.info("点击赞同")
                                await button_agree.click()
                                await asyncio.sleep(3)
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
                    try:
                        await self.page.keyboard.press(
                            "Escape")  # 这里也报错了：playwright._impl._errors.Error: ElementHandle.click: Element is not attached to the DOM
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
                    await self.page.keyboard.press("Escape")
                    await self.page.keyboard.press("Escape")

                    logging.info("进入分享区")
                    button_share = await selector_one.query_selector('.Button:has-text("分享")')
                    if button_share is not None:
                        if share:
                            logging.info("点击分享")
                            await button_share.click()
                            await asyncio.sleep(3)
                            # 复制链接
                            button_share_link = await self.page.query_selector(
                                'xpath=//button[@class="Button Menu-item ShareMenu-button Button--plain" and contains(text(), "复制链接")]')
                            if button_share_link is not None:
                                await button_share_link.click()
                                await asyncio.sleep(3)

                    logging.info("进入收藏区")
                    button_collection = await selector_one.query_selector('.Button:has-text("收藏")')
                    if button_collection is not None:
                        if collection:
                            logging.info("点击收藏")
                            await button_collection.click()
                            await asyncio.sleep(3)
                            # 选择收藏夹
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
                                await submit.click()
                                await asyncio.sleep(3)
                        # 按ESC键退出升级页面
                        await self.page.keyboard.press("Escape")
                        await self.page.keyboard.press("Escape")
                        await self.page.keyboard.press("Escape")
                        await asyncio.sleep(3)

                    # 点击私信 TODO

                    logging.info("点击推荐进行刷新页面")
                    link_locator = await self.page.query_selector('.TopstoryTabs-link:has-text("推荐")')
                    try:
                        if link_locator:
                            await link_locator.click()
                            await asyncio.sleep(5)
                            continue
                    except:
                        logging.info("没刷新也无所谓")
                        pass
                    pass
                    logging.info("滚动页面")
                    for i in range(6):
                        await self.page.wait_for_load_state()
                        await self.page.mouse.wheel(0, 50)  # 每次滚动100像素
                        await asyncio.sleep(1)
                    await self.page.keyboard.press("Escape")
                    await self.page.keyboard.press("Escape")
                logging.info("浏览时间结束，再见")

                # 添加到数据库
                data = {
                    'account_name': self.account_name,
                    'type': self.type,
                    'duration': self.duration,
                    'status': 1,
                    'date': datetime.date.today(),
                    'datetime': datetime.datetime.now(),
                }
                await insert(pool=self.pool, table_name='random_browsing', data=data)
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
    file_handler = logging.FileHandler(filename=os.path.join(logs_dir, f'random_browsing_{datetime.date.today()}.log'),
                                       mode='a', encoding='utf-8')
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
            recommend = RandomBrowsing(pool=pool, html_lock=html_lock, command=find['command'],
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


    while True:
        asyncio.run(start())
