"""
消息邀请问题回答-控制器
2024年9月13日21:55:02 调试通过
"""
import asyncio
import datetime
import logging
import os
import subprocess
import traceback
from asyncio import Lock

import aiomysql
import pyperclip
from playwright.async_api import async_playwright
from modules.zhihu.api.resource.zhihu_prompt import ZhihuPrompt
from modules.zhihu.chat.api import chat
from db.mysql.mysql_jdbc import insert, select_list, create_pool, close_pool
from modules.zhihu.api.resource.resources_service import ResourcesService
from modules.zhihu.api.utils.common_utils import close_browser_by_domain, kill_process_by_port, \
    kill_processes_by_user_data_dir, ping_website
from db.mysql.mysql_jdbc import insert, select_list, create_pool
from modules.zhihu.plugin_email.email_notice import email_notification
from modules.zhihu.plugin_screenshot.screenshot_page_element import screenshot_page


from modules.zhihu.api.functions import current_directory
util_html_path = os.path.join(current_directory, "html_utils", "util.html")
markdown_html_path = os.path.join(current_directory, "html_utils", "markdown.html")


class PostAnswersMessageInvitation:
    task_type = 4

    def __init__(self, pool, html_lock: Lock, command: str, account_username: str, account_name: str,
                 user_data_dir_path: str,
                 remote_debugging_port: int, browser_type: str, hide: bool = False, mock_text=None):
        self.pool = pool
        self.html_lock = html_lock
        self.resourcesService = None  # 需要用到数据库，只能异步初始化，无法在同步的init中。
        self.url = "https://www.zhihu.com/notifications"
        self.type = "PostAnswersMessageInvitation"
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
                while True:
                    await asyncio.sleep(1)
                    logging.info(f"请登录:{datetime.datetime.now()}")
                    if self.page.url.startswith('https://www.zhihu.com/signin'):
                        if await self.page.locator('input[placeholder="手机号"]').is_visible():
                            value = await self.page.locator('input[placeholder="手机号"]').input_value()
                            if value != self.account_name:
                                await self.page.locator('input[placeholder="手机号"]').fill(self.account_name)
                            # 这里要发消息进行提醒。TODO,进行截图发邮件，这样可以远程扫码登录。
                            continue
                        else:
                            break
                    else:
                        break
                await asyncio.sleep(1)
                logging.info("登录成功！")
                await self.page.wait_for_load_state('networkidle')

                # 检查包含特定文本的元素是否存在
                while True:
                    element_upgrade = await self.page.query_selector_all('text="系统升级中，请稍后再试"')
                    if len(element_upgrade) > 0:
                        await asyncio.sleep(10)
                        # 等待10秒，刷新页面
                        await self.page.reload()
                    else:
                        break

                logging.info("点击全部类别")
                button_locator = await self.page.query_selector('#Popover3-toggle')
                await button_locator.click()
                await asyncio.sleep(3)
                selection_locator = await self.page.query_selector(
                    '.Button.Menu-item.Notifications-MenuItem.Button--plain:has-text("邀请")')
                logging.info("点击‘邀请’")
                await selection_locator.click()
                await asyncio.sleep(3)

                logging.info("获取邀请列表")
                xpath1 = 'xpath=//div[@class="NotificationList css-0" and @role="list"]//div[@class="NotificationList-Item-content"]//a[@class="NotificationList-Item-link" and @role="button"]'
                xpath2 = '//div[@class="NotificationList css-0" and @role="list"]//time[@class="NotificationList-DateSplit"]'
                invitation_selector_all = await self.page.query_selector_all(xpath1 + " | " + xpath2)
                contents = []
                for i in invitation_selector_all:
                    text_content = await i.text_content()
                    if text_content.count("-") == 2:
                        contents.append(text_content)
                    else:
                        attribute = await i.get_attribute("href")
                        contents.append(attribute)
                pass

                def get_data_group_by_date(a):
                    b = {}
                    # 用于存储当前日期和问题列表
                    current_date = None
                    current_list = []

                    for item in a:

                        if isinstance(item, str) and item.count("-") == 2:  # 判断是否为日期
                            if current_date:  # 如果当前已经有一个日期和问题列表，存储到字典中
                                b[current_date] = current_list
                            current_date = item  # 更新当前日期
                            current_list = []  # 重置问题列表，当前日期作为第一个元素
                        else:
                            current_list.append(item)  # 将问题添加到问题列表中

                    # 存储最后一个日期的问题列表
                    if current_date:
                        b[current_date] = current_list

                    return b

                logging.info("按时间归类")
                data_group_by_date = get_data_group_by_date(contents)
                today = datetime.datetime.now()
                # 计算昨天的日期
                yesterday = today - datetime.timedelta(days=1)
                # 格式化日期为 YYYY-MM-DD 格式
                yesterday_str = yesterday.strftime('%Y-%m-%d')

                logging.info("遍历昨天的邀请")
                if len(data_group_by_date[yesterday_str]) == 0:
                    return {"code": False, "message": "昨天收到的邀请为0"}
                for question_url in data_group_by_date[yesterday_str]:

                    await self.page.goto("https://www.zhihu.com/notifications")
                    await asyncio.sleep(3)
                    # 点击全部类别
                    button_locator = await self.page.query_selector('#Popover3-toggle')
                    await button_locator.click()
                    await asyncio.sleep(3)
                    selection_locator = await self.page.query_selector(
                        '.Button.Menu-item.Notifications-MenuItem.Button--plain:has-text("邀请")')
                    await selection_locator.click()
                    await asyncio.sleep(3)
                    # 获取邀请的话题
                    xpath = 'xpath=//div[@class="NotificationList css-0" and @role="list"]//div[@class="NotificationList-Item-content"]//a[@class="NotificationList-Item-link" and @role="button"]'
                    invitation_selector_all = await self.page.query_selector_all(xpath)
                    question_selector = None
                    for invitation in invitation_selector_all:
                        if await  invitation.get_attribute("href") == question_url:
                            question_selector = invitation

                    await question_selector.click()
                    await asyncio.sleep(3)

                    logging.info("检测一下是否已经回答过")
                    check_selector = await self.page.query_selector('a[type="button"]:has-text("查看我的回答")')
                    if check_selector is not None:
                        logging.info(f"已经回答过了，跳过")
                        continue
                    button_selector = 'button[type="button"] >> text="写回答"'
                    query_selector = await self.page.query_selector(button_selector)
                    if query_selector is None:
                        logging.info(f"已经回答过了，跳过")
                        continue
                    await query_selector.click()
                    # 问题标题
                    h1_locator = await self.page.query_selector('h1.QuestionHeader-title')
                    gpt_param = {"question_content": "", 'question_title': await h1_locator.text_content()}
                    # 获取元素文本
                    logging.info("检测是否重复回答")
                    async with self.pool.acquire() as conn:
                        async with conn.cursor(aiomysql.DictCursor) as cur:
                            await cur.execute(
                                f'SELECT count(*) as `count` FROM post_answers where account_name="{self.account_name}" and question_title like "%{gpt_param["question_title"]}%"')  # 这里会注入，An error occurred: (1064, 'You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near \'大哥"吗？%"\' at line 1')
                            count = await cur.fetchone()
                            if count["count"] > 0:
                                logging.info(f"问题已回答过，跳过: {gpt_param['question_title']}")
                                continue

                    selector = await self.page.query_selector("text=添加谢邀")
                    if selector is not None:
                        logging.info("添加谢邀")
                        await selector.click()
                    # 显示全部
                    await asyncio.sleep(3)
                    # 显示全部的按钮
                    button_display_all = await self.page.query_selector('text="显示全部"')
                    # 如果按钮存在，则点击
                    if button_display_all:
                        logging.info("点击显示全部按钮")
                        await button_display_all.click()
                        await asyncio.sleep(1)

                    div_locator = await self.page.query_selector('.QuestionRichText--expandable')
                    logging.info("检查元素是否存在")
                    if div_locator:
                        # 使用text_content()获取文本
                        gpt_param['question_content'] = await div_locator.text_content()
                    else:
                        logging.info("元素不存在")
                    pass
                    # 关键字避障 比如 AI、人工智能
                    logging.info("进行关键字避障检测【AI、人工智能、大模型、智能助手、GPT】")
                    if 'ai' in gpt_param['question_title'] or 'ai' in gpt_param['question_content']:
                        continue
                    if 'AI' in gpt_param['question_title'] or 'AI' in gpt_param['question_content']:
                        continue
                    if 'Ai' in gpt_param['question_title'] or 'Ai' in gpt_param['question_content']:
                        continue
                    if '人工智能' in gpt_param['question_title'] or '人工智能' in gpt_param['question_content']:
                        continue
                    if 'GPT' in gpt_param['question_title'] or 'GPT' in gpt_param['question_content']:
                        continue
                    if '大模型' in gpt_param['question_title'] or '大模型' in gpt_param['question_content']:
                        continue
                    if '智能助手' in gpt_param['question_title'] or '智能助手' in gpt_param['question_content']:
                        continue
                    if gpt_param['question_content'] is None or gpt_param['question_content'] == "":
                        question = f"我的问题是：'{gpt_param['question_title']}'，请帮我做出一个回答或建议，越详细越好"
                    else:
                        question = f"我的问题是：'{gpt_param['question_title']}'，问题的补充是：'{gpt_param['question_content']}'，请帮我做出一个回答或建议，回答内容不要重复我的问题，直接给我内容即可，越详细越好"

                    result = None
                    m = '模拟'
                    prompt = None
                    if self.mock_text is not None:
                        result = self.mock_text
                    else:
                        prompt = ZhihuPrompt.get_answer_prompt(self.account_name, 800)
                        logging.info(f"向GPT请求答案")
                        result, m = await chat(self.pool, prompt, question)
                    logging.info(f"【{m}】回答：{result}")
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
                        logging.info("粘贴原始文本")
                        # 全选文本
                        await page_json.keyboard.down('Control')
                        await page_json.keyboard.press('A')
                        await page_json.keyboard.up('Control')
                        await page_json.keyboard.press('Delete')
                        # 粘贴文本
                        await page_json.keyboard.down('Control')
                        await page_json.keyboard.press('V')
                        await page_json.keyboard.up('Control')

                        await page_json.close()
                        logging.info("回到知乎文本框中")
                        all_pages = self.content.pages
                        self.page = all_pages[1]

                        # 定位富文本编辑器
                        contenteditable_selector = 'div[contenteditable="true"]'
                        # 聚焦编辑器
                        await self.page.focus(contenteditable_selector)
                        logging.info("粘贴文本")
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
                                                                              type="PostAnswersMessageInvitation",
                                                                              pic_number=3)
                    if pictures:
                        await asyncio.sleep(3)
                        logging.info("点击上传图片")
                        button_locator = await self.page.query_selector('button[type="button"][aria-label="图片"]')
                        try:
                            await button_locator.click()
                        except:
                            pass
                        await asyncio.sleep(3)

                        # 定位上传标签
                        file_input_selector = 'xpath=//input[@type="file" and @accept="image/*"]'
                        try:
                            await self.page.set_input_files(file_input_selector,
                                                            pictures)  # TODO 经常 ！！！ 这里会报错：Timeout 30000ms exceeded.waiting for locator("//input[@type=\"file\" and @accept=\"image/*\"]")，playwright._impl._errors.TimeoutError: Page.set_input_files: Timeout 30000ms exceeded.
                        except:
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

                    try:
                        # 是否存在赞赏功能
                        appreciate_setting_selector = await self.page.query_selector('label >> text="赞赏设置"')
                        if appreciate_setting_selector is not None:
                            logging.info("试图开启赞赏功能")
                            # 开启赞赏
                            open_appreciate = await self.page.query_selector(
                                'label[for="PublishPanel-RewardSetting-0"]')
                            # 关闭赞赏
                            # close_appreciate = self.page.query_selector('label[for="PublishPanel-RewardSetting-1"]')
                            await open_appreciate.click()
                            await asyncio.sleep(3)
                            # 同意协议
                            modal_inner_selector = await self.page.query_selector('div.Modal-inner')
                            agree_selector = await modal_inner_selector.query_selector(
                                'button[type="button"] >> text="确定"')
                            await agree_selector.click()
                            await asyncio.sleep(3)
                    except:
                        traceback.print_exc()
                        exc_info = traceback.format_exc()
                        pass
                    # 按ESC键退出升级页面
                    await self.page.keyboard.press("Escape")
                    await self.page.keyboard.press("Escape")
                    await self.page.keyboard.press("Escape")

                    # 定位发布按钮
                    button_selector = 'button[type="button"] >> text="发布回答"'
                    await asyncio.sleep(10)
                    logging.info("发布回答")
                    await self.page.click(button_selector)
                    for i in range(10):
                        logging.info(f"循环检测是否出现‘您的回答过于频繁’{i}")
                        sos = await self.page.query_selector_all(
                            '.Notification-textSection:has-text("您的回答过于频繁")')
                        if sos is not None and len(sos) > 0:
                            pass
                            logging.info("注意！注意！注意！检测到回答过于频繁！！！！")
                            return {"code": False, "message": "您的回答过于频繁"}
                    await self.page.wait_for_load_state('networkidle')
                    # 这里要校验一下是不是发布成功
                    is_success = False
                    for i in range(10):
                        await asyncio.sleep(1)
                        # 这里要校验一下是不是发布成功
                        qs = await self.page.query_selector(
                            'a[role="button"][tabindex="0"].AnswerItem-editButton')
                        is_success = qs is not None and await qs.query_selector(
                            'span.AnswerItem-editButtonText >> text="修改"') is not None
                        if is_success:
                            break
                    logging.info(f"校验是否发布成功:{is_success}")
                    self.resourcesService.del_pictures(pictures)
                    logging.info(f"记录发布历史")
                    data = {
                        'account_name': self.account_name,
                        'type': self.type,
                        'question_title': gpt_param['question_title'],
                        'status': 1,
                        'is_success': False,
                        'date': datetime.date.today(),
                        'datetime': datetime.datetime.now(),
                    }
                    await insert(pool=self.pool, table_name='post_answers', data=data)

                    return {"code": is_success,
                            "message": "顺利走完流程" if is_success else "顺利走完流程，但是未检测到发布成功"}
                return {"code": False,
                        "message": "所有的回答链接都在遍历时跳过了，不是回答过了就是GPT一直回答不了，总之没有一个走完的"}
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
    data = """### 创造力：大脑的可塑性与训练的可能性

嘿，朋友！你问了一个超级棒的问题！创造力，这个看似神秘的东西，其实是可以通过训练来提升的。大脑的可塑性意味着，即使成年后，我们依然可以通过一些方法来唤醒和增强我们的创造力。让我来给你详细解析一下，如何通过日常的训练来提升你的创造力吧！

#### 1. **大脑的可塑性：基础概念**

首先，大脑的可塑性是指大脑在结构和功能上的变化能力。这种能力不仅在儿童时期存在，成年后依然可以发挥作用。这意味着，通过适当的训练，我们可以改变大脑的某些区域，从而提升我们的创造力。

#### 2. **创造力的训练方法**

##### 2.1 **多感官体验**

多感官体验是提升创造力的一个重要方法。通过视觉、听觉、触觉等多种感官的刺激，可以激发大脑的多个区域，从而促进创造性思维的产生。

- **视觉刺激**：每天花时间观察周围的环境，尝试从不同的角度看待事物。比如，你可以尝试用不同的颜色和形状来重新装饰你的房间。
- **听觉刺激**：听一些不同类型的音乐，尤其是那些你平时不太接触的音乐风格。音乐的节奏和旋律可以激发你的大脑，产生新的想法。
- **触觉刺激**：尝试用手去感受不同的材质，比如沙子、水、布料等。这种触觉的多样性可以帮助你更好地理解事物的本质。

##### 2.2 **思维导图**

思维导图是一种非常有效的创造力训练工具。通过将你的想法以图形化的方式呈现出来，可以帮助你更好地组织和连接不同的概念。

- **每天绘制思维导图**：选择一个主题，比如“未来的生活”，然后开始绘制思维导图。你可以从中心点开始，逐步扩展出不同的分支，每个分支代表一个相关的想法。
- **自由联想**：在绘制思维导图时，不要限制自己的思维，尽可能多地进行自由联想。即使有些想法看起来不相关，也不要轻易放弃，因为它们可能会在后续的思考中产生新的联系。

##### 2.3 **逆向思维**

逆向思维是一种非常有用的创造力训练方法。通过反向思考问题，你可以打破常规的思维模式，从而产生新的解决方案。

- **反向思考**：每天选择一个问题或任务，然后尝试从反方向去思考。比如，如果你通常会考虑如何解决问题，那么你可以尝试思考如何让问题变得更严重，然后再从中找到解决方案。
- **挑战常规**：不要害怕挑战现有的规则和惯例。通过质疑和重新定义问题，你可以发现新的可能性。

##### 2.4 **创意写作**

创意写作是提升创造力的另一个有效方法。通过写作，你可以更好地表达和组织你的想法，同时也可以激发新的灵感。

- **每天写作**：每天花15-30分钟进行创意写作。你可以选择一个随机的主题，然后开始写作。不要担心语法或逻辑，重要的是让你的思维自由流动。
- **故事创作**：尝试创作一些短篇故事或小说。通过构建一个完整的故事情节，你可以锻炼你的想象力和创造力。

#### 3. **实践中的成熟训练方案**

在实践中，有一些成熟的训练方案可以帮助你提升创造力。这些方案通常结合了多种方法，旨在全面提升你的创造性思维能力。

| 训练方案 | 具体方法 | 效果 |
| --- | --- | --- |
| 多感官体验训练 | 每天进行视觉、听觉、触觉的多样性体验 | 提升大脑的灵活性和创造性思维 |
| 思维导图训练 | 每天绘制思维导图，进行自由联想 | 帮助组织和连接不同的概念，激发新的想法 |
| 逆向思维训练 | 每天进行反向思考，挑战常规 | 打破常规思维模式，产生新的解决方案 |
| 创意写作训练 | 每天进行创意写作，故事创作 | 提升表达能力和想象力，激发新的灵感 |

#### 4. **每天坚持的具体方法**

为了确保这些方法能够持续发挥作用，你需要每天坚持进行这些训练。以下是一些具体的建议：

- **设定固定时间**：每天设定一个固定的时间段进行创造力训练，比如早上起床后或晚上睡觉前。
- **记录进展**：每天记录你的训练进展和新的想法。这不仅可以帮助你保持动力，还可以让你看到自己的进步。
- **寻找伙伴**：找一个志同道合的朋友一起进行创造力训练。你们可以互相激励，分享彼此的想法和进展。

#### 5. **总结**

创造力并不是天生的，而是可以通过训练来提升的。通过多感官体验、思维导图、逆向思维和创意写作等方法，你可以逐步唤醒和增强你的创造力。记住，大脑的可塑性意味着你可以在任何年龄段提升自己的创造力。所以，不要犹豫，从今天开始，让你的大脑变得更加灵活和富有创造力吧！

希望这些建议对你有所帮助！如果你有任何问题或想法，随时欢迎和我交流！"""
    import nest_asyncio

    # 创建日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logs_dir = fr'logs\{datetime.date.today()}'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    # 创建文件处理器，将日志写入文件
    file_handler = logging.FileHandler(
        filename=os.path.join(logs_dir, f'post_answers_message_invitation_{datetime.date.today()}.log'), mode='a',
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
            recommend = PostAnswersMessageInvitation(pool=pool, html_lock=html_lock, command=find['command'],
                                                     account_username=account['username'],
                                                     account_name=account['account_name'],
                                                     remote_debugging_port=account['remote_debugging_port'],
                                                     browser_type=account['browser_type'], hide=False)
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
