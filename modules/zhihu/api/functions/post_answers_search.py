"""
回答搜索问题-控制器
2024年9月19日08:48:52 测试通过
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
from modules.zhihu_auto.api.resource.zhihu_prompt import ZhihuPrompt
from modules.zhihu_auto.chat.api import chat
from db.mysql.mysql_jdbc import insert, select_list, create_pool, close_pool
from modules.zhihu_auto.api.resource.resources_service import ResourcesService
from modules.zhihu_auto.api.utils.common_utils import close_browser_by_domain, kill_process_by_port, \
    kill_processes_by_user_data_dir, ping_website
from db.mysql.mysql_jdbc import insert, select_list, create_pool
from modules.zhihu_auto.plugin_email.email_notice import email_notification
from modules.zhihu_auto.plugin_screenshot.screenshot_page_element import screenshot_page



from modules.zhihu_auto.api.functions import current_directory
util_html_path = os.path.join(current_directory, "html_utils", "util.html")
markdown_html_path = os.path.join(current_directory, "html_utils", "markdown.html")


class PostAnswersSearch:
    """
    回答
    """

    def __init__(self, pool, html_lock: Lock, command: str, account_username: str, account_name: str,
                 remote_debugging_port: int, browser_type: str,
                 label: str = "擅长话题", draft: bool = False, hide: bool = False, mock_text=None):
        """
        :param pool 数据库连接池
        :param html_lock: 互斥锁
        :param command: 命令
        :param account_username: 账号
        :param account_name: 账号名称
        :param remote_debugging_port: 远程调试端口
        :param browser_type: 浏览器类型
        :param label 回答类型
        :param draft: 是否为草稿
        :param mock_text: 模拟答案
        :return:
        """
        self.pool = pool
        self.html_lock = html_lock
        self.resourcesService = None  # 需要用到数据库，只能异步初始化，无法在同步的init中。
        self.label = label
        self.draft = draft
        self.type = f"PostAnswers{label}"
        self.command = command
        if hide:
            self.command = command + " --window-position=10000,10000 "
        self.url = "https://www.zhihu.com/creator/featured-question/recommend"
        self.account_username = account_username
        self.account_name = account_name
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

                # 监测一下是不是登录页面，如果是登录页面，则在页面上标记账号，并定期循环监测，直到登录成功。
                while True:
                    await asyncio.sleep(1)
                    logging.info(f"请登录:{datetime.datetime.now()}")
                    if self.page.url.startswith('https://www.zhihu.com/signin'):

                        if await self.page.locator('input[placeholder="手机号"]').is_visible():
                            value = await  self.page.locator('input[placeholder="手机号"]').input_value()
                            if value != self.account_name:
                                await self.page.locator('input[placeholder="手机号"]').fill(self.account_name)
                            pass
                            # 这里要发消息进行提醒。TODO,进行截图发邮件，这样可以远程扫码登录。
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

                logging.info(f"进行【{self.label}】标签切换")
                if not await self.page.query_selector(f"text={self.label}"):
                    logging.info(f"没有开启{self.label}，直接结束")
                    return {"code": False, "message": f"未开通 {self.label}栏目"}
                else:
                    logging.info("标签切换中")
                    await self.page.wait_for_selector(f"text={self.label}")
                    qs = await self.page.query_selector(f"text={self.label}")
                    await qs.click()
                    await self.page.wait_for_load_state('networkidle')
                logging.info("定位问题列表")
                locators_all = []
                for i in range(3):
                    await asyncio.sleep(1)
                    locators_all = await self.page.locator('div[role="list"]').locator(
                        'div[class="css-vurnku"]').locator(
                        'a').all()
                    if len(locators_all) > 0:
                        break
                hrefs = []
                # 筛选出有+10分的问题
                hrefs_10 = []
                hrefs_20 = []
                for i in locators_all:
                    handle = await i.element_handle()
                    selector = await handle.query_selector("xpath=../../..")
                    text_content = await selector.text_content()
                    if '+10分' in text_content:
                        hrefs_10.append(i.get_attribute("href"))
                    if '+20分' in text_content:
                        hrefs_20.append(i.get_attribute("href"))
                # 优先采用+20的
                if len(hrefs_20) > 0:
                    hrefs = hrefs_20
                # 如果一个+20分都没有，就采用+10的
                if len(hrefs) == 0:
                    hrefs = hrefs_10
                # 如果一个+10分都没有，那就随便吧
                if len(hrefs) == 0:
                    hrefs = [await ai.get_attribute("href") for ai in locators_all if await ai.get_attribute("href")]
                if len(hrefs) == 0:
                    logging.info("获取到的回答链接为0，是不是定位出了问题？")
                    return {"code": False, "message": "获取到的回答链接为0，是不是定位出了问题？"}
                for index, href in enumerate(hrefs):
                    logging.info(f"处理问题链接: {href}")
                    await self.page.goto(href)
                    await asyncio.sleep(3)
                    # 检测一下是否已经回答过
                    check_selector = await  self.page.query_selector('a[type="button"]:has-text("查看我的回答")')
                    if check_selector is not None:
                        logging.info(f"已经回答过了，跳过")
                        continue
                    # 问题标题
                    h1_locator = await  self.page.query_selector('h1.QuestionHeader-title')
                    gpt_param = {"question_title": await  h1_locator.text_content(), "question_content": ""}
                    # condition = {
                    #     'account_name': self.account_name,
                    #     'question_title': gpt_param["question_title"]
                    # }
                    # count = await select_count(pool=self.pool, table_name='post_answers', condition=condition)
                    # 检测重复,是否已经回答过这个问题
                    async with self.pool.acquire() as conn:
                        async with conn.cursor(aiomysql.DictCursor) as cur:
                            await cur.execute(
                                f'SELECT count(*) as `count` FROM post_answers where account_name="{self.account_name}" and question_title like "%{gpt_param["question_title"]}%"')  # 这里会注入，An error occurred: (1064, 'You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near \'大哥"吗？%"\' at line 1')
                            count = await cur.fetchone()
                            if count["count"] > 0:
                                logging.info(f"问题已回答过，跳过: {gpt_param['question_title']}")
                                continue

                    # 显示全部
                    await asyncio.sleep(3)
                    # 显示全部的按钮
                    button_display_all = await  self.page.query_selector('text="显示全部"')
                    # 如果按钮存在，则点击
                    if button_display_all:
                        logging.info("点击显示全部按钮")
                        await button_display_all.click()
                        await asyncio.sleep(1)

                    div_locator = await  self.page.query_selector('.QuestionRichText--expandable')
                    # 检查元素是否存在
                    if div_locator:
                        # 使用text_content()获取文本
                        gpt_param['question_content'] = await div_locator.text_content()
                    else:
                        logging.warning("元素不存在")
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
                        question = f"我的问题是：'{gpt_param['question_title']}'，问题的补充是：'{gpt_param['question_content']}'，回答内容不要重复我的问题，直接给我内容即可，请帮我做出一个回答或建议，越详细越好"
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
                    if result is None:
                        continue
                    logging.info("记录一下GPT回答的历史,用于溯源")
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
                        # 现将文本输入
                        logging.info("利用页面进行markdown格式转换")
                        page_json = await  self.content.new_page()
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
                        logging.info("点击写回答按钮")
                        await self.page.locator(
                            'xpath=//main[@class="App-main"]//div[@class="QuestionHeader"]//button[contains(text(),"写回答")]').click()
                        # 定位富文本编辑器
                        contenteditable_selector = 'div[contenteditable="true"]'
                        # 聚焦编辑器
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

                    # 使用 page.set_input_files 上传文件
                    pictures = await self.resourcesService.get_three_pictures(account_username=self.account_username,
                                                                              account_name=self.account_name,
                                                                              type=self.type,
                                                                              pic_number=3)
                    if pictures:
                        logging.info("准备上传图片")
                        # 点击上传图片
                        button_locator = await self.page.query_selector('button[type="button"][aria-label="图片"]')
                        # 这里可能定位不到 TODO
                        try:
                            await button_locator.click()
                        except:
                            pass
                        await asyncio.sleep(3)
                        # 定位上传标签
                        file_input_selector = 'xpath=//input[@type="file" and @accept="image/*"]'
                        logging.info(f"上传图片: {pictures}")
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
                        logging.info("插入推片，睡一会")
                        await asyncio.sleep(20)
                    try:
                        # 是否存在赞赏功能
                        appreciate_setting_selector = await self.page.query_selector('label >> text="赞赏设置"')
                        if appreciate_setting_selector is not None:
                            # 开启赞赏
                            open_appreciate = await self.page.query_selector(
                                'label[for="PublishPanel-RewardSetting-0"]')
                            # 关闭赞赏
                            # close_appreciate = self.page.query_selector('label[for="PublishPanel-RewardSetting-1"]')
                            await open_appreciate.click()
                            await self.page.wait_for_selector('div.Modal-inner', timeout=1000 * 3)
                            # 同意协议
                            modal_inner_selector = await self.page.query_selector('div.Modal-inner')
                            agree_selector = await modal_inner_selector.query_selector(
                                'button[type="button"] >> text="确定"')
                            await agree_selector.click()
                            await self.page.wait_for_load_state('networkidle')
                            logging.info("开启了赞赏功能")
                    except:
                        logging.info("赞赏功能失败（可能已经处于开启状态）")
                        pass
                    # 按ESC键退出升级页面
                    await self.page.keyboard.press("Escape")
                    await self.page.keyboard.press("Escape")
                    await self.page.keyboard.press("Escape")

                    data = {
                        'account_name': self.account_name,
                        'type': self.type,
                        'question_title': gpt_param['question_title'],
                        'status': 1,
                        'is_success': False,
                        'date': datetime.date.today(),
                        'datetime': datetime.datetime.now(),
                    }

                    if not self.draft:
                        # 定位发布按钮
                        button_selector = 'button[type="button"] >> text="发布回答"'
                        # 点击发布
                        logging.info("点击发布回答按钮")
                        await self.page.click(button_selector)
                        for i in range(10):
                            logging.info(f"循环检测是否出现‘您的回答过于频繁’{i}")
                            sos = await  self.page.query_selector_all(
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
                            qs = await self.page.query_selector('a[role="button"][tabindex="0"].AnswerItem-editButton')
                            is_success = qs is not None and await qs.query_selector(
                                'span.AnswerItem-editButtonText >> text="修改"') is not None
                            if is_success:
                                break
                        logging.info(f"校验是否发布成功:{is_success}")
                        logging.info(f"记录发布历史")
                        data['is_success'] = is_success
                    await self.resourcesService.del_pictures(pictures)
                    await insert(pool=self.pool, table_name='post_answers', data=data)

                    return {"code": True, "message": "顺利走完流程"}
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
            except Exception as e:
                logging.error(f"Failed to clean up resources: {e}")


if __name__ == '__main__':
    data = """### 创造力：大脑的可塑性与训练的可能性

嘿，朋友！你问了一个超级棒的问题！创造力，这个看似神秘的东西，其实是可以通过训练来提升的。大脑的可塑性意味着，即使成年后，我们依然可以通过一些方法来唤醒和增强我们的创造力。让我来给你详细解析一下，如何通过日常的训练来提升你的创造力吧！

#### 1. **大脑的可塑性：基础概念**

首先，大脑的可塑性是指大脑在结构和功能上的变化能力。这种能力不仅在儿童时期存在，成年后依然可以发挥作用。这意味着，通过适当的训练，我们可以改变大脑的某些区域，从而提升我们的创造力。

#### 2. **创造力的训练方法**
"""
    import nest_asyncio

    # 创建日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logs_dir = fr'logs\{datetime.date.today()}'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    # 创建文件处理器，将日志写入文件
    file_handler = logging.FileHandler(
        filename=os.path.join(logs_dir, f'post_answers{datetime.date.today()}.log'),
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
            recommend = PostAnswersSearch(pool=pool, html_lock=html_lock, command=find['command'],
                                          account_username=account['username'],
                                          account_name=account['account_name'],
                                          remote_debugging_port=account['remote_debugging_port'],
                                          browser_type=account['browser_type'], label="擅长话题", draft=False,
                                          hide=False)
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
