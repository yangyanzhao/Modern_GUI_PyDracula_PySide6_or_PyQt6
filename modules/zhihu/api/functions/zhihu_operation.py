import asyncio
import datetime
import logging
import os
import random
import traceback
from asyncio import Lock
from collections import defaultdict

from gui.utils.tinydb_util import build_query
from gui.widgets.c_table_view_widget.table_view_tinydb_widget import TableViewWidgetTinyDBAbstract
from modules.zhihu_auto.api.functions import pictures_file_path
from modules.zhihu_auto.api.functions.ask_questions import AskingQuestions
from modules.zhihu_auto.api.functions.follow import Follow
from modules.zhihu_auto.api.functions.follow_recommend import FollowRecommend
from modules.zhihu_auto.api.functions.post_answers import PostAnswers
from modules.zhihu_auto.api.functions.post_answers_message_invitation import PostAnswersMessageInvitation
from modules.zhihu_auto.api.functions.publish_article import PublishArticle
from modules.zhihu_auto.api.functions.publish_ideas import PublishIdeas
from modules.zhihu_auto.api.functions.random_browsing import RandomBrowsing
from modules.zhihu_auto.api.functions.refresh_likes import RefreshLikes
from modules.zhihu_auto.api.resource.douyin_hot_topic_spider import DouyinHotTopicSpider
from modules.zhihu_auto.api.resource.picture_pixabay_spider import PicturePixabaySpider
from modules.zhihu_auto.api.resource.resources_service import ResourcesService
from modules.zhihu_auto.api.resource.weibo_hot_topic_spider import WeiboHotTopicSpider
from modules.zhihu_auto.api.utils.common_utils import find_chrome_path, find_edge_path, kill_process_by_name
from db.mysql.mysql_jdbc import update_by_id, select_list, insert_batch, create_pool, \
    close_pool, select_list_by_database_table
from modules.zhihu_auto.api.functions import current_directory

util_html_path = os.path.join(current_directory, "html_utils", "util.html")
markdown_html_path = os.path.join(current_directory, "html_utils", "markdown.html")


# 获取command,用于生成计划任务
def get_command(user_data_dir_path, browser_type, remote_debugging_port):
    browser_path = None
    if browser_type == "chrome.exe":
        browser_path = find_chrome_path()
    elif browser_type == "msedge.exe":
        browser_path = find_edge_path()
    else:
        raise Exception("浏览器类型错误或者未填写")
    CHROME_PATH = f'"{browser_path}"'
    user_data_dir = os.path.expanduser(user_data_dir_path)
    os.makedirs(user_data_dir, exist_ok=True)
    # 远程调试端口
    debugging_port = f"--remote-debugging-port={remote_debugging_port}"
    # 指定用户数据目录
    user_data_dir_arg = f"--user-data-dir={user_data_dir}"
    # 启动最大化
    start_maximized_arg = "--start-maximized"
    # 隐藏
    hide = "--window-position=10000,10000"
    # 总体指令
    command = fr"{CHROME_PATH} {debugging_port} {user_data_dir_arg} {start_maximized_arg}"
    return command


async def generate_plan_(account, task_setting_list, is_reset=False):
    """
    生成任务（自带连接池）
    """
    try:
        await generate_plan(account=account, task_setting_list=task_setting_list, is_reset=is_reset)
    except:
        traceback.print_exc()
        error = traceback.format_exc()


# 根据账号ID生成任务
async def generate_plan(account, task_setting_list, is_reset=False):
    command = get_command(user_data_dir_path=account['user_data_dir_path'], browser_type=account['browser_type'],
                          remote_debugging_port=account['remote_debugging_port'])
    # 生成账号命令
    account['command'] = command

    # 账号配置
    # 由于tinydb没有id字段，只有外部的doc_id字段，这里我们主观的加入id字段
    tasks = task_setting_list
    task = {}
    # 遍历列表中的每个字典
    for d in tasks:
        # 遍历当前字典的键
        for key in d:
            # 如果键已经在结果字典中，则相加；否则直接赋值
            if key in task:
                task[key] += d[key]
            else:
                task[key] = d[key]
    recommend_number: int = int(task['post_answers_recommend'])  # 推荐回答数量
    good_at_number: int = int(task['post_answers_good_at'])  # 擅长回答数量
    invited_number: int = int(task['post_answers_invited'])  # 邀请回答数量
    message_invitation_number: int = int(task['post_answers_message_invitation'])  # 消息回答数量
    new_number: int = int(task['post_answers_new'])  # 最新回答数量
    mcn_number: int = int(task['post_answers_mcn'])  # 种草回答数量
    draft_good_at_number: int = int(task['draft_post_answers_good_at'])  # 草稿回答数量
    article_number: int = int(task['publish_article'])  # 发布文章数量
    draft_article_number: int = int(task['draft_publish_article'])  # 草稿文章数量
    ideas_number: int = int(task['publish_ideas'])  # 想法数量
    asking_questions_number: int = int(task['asking_questions'])  # 提问数量
    follow_number: int = int(task['follow'])  # 任务关注数量
    follow_recommend_number: int = int(task['follow_recommend'])  # 推荐关注数量
    refresh_likes_number: int = int(task['refresh_likes'])  # 任务关注数量
    random_browsing_number: int = int(task['random_browsing'])  # 漫游数量
    # 查出每一项的数量，然后减去已经生成的。
    reduces = select_list_by_database_table(database_name='zhihu', table_name='task_plan',
                                            conditions=[{'field': 'account_id', 'value': account['id'], 'op': 'eq'},
                                                        {'field': 'plan_date',
                                                         'value': datetime.datetime.today().strftime("%Y-%m-%d"),
                                                         'op': 'eq'}])
    # reduces进行分组
    grouped = defaultdict(int)
    # 遍历字典列表，根据 'category' 字段进行分组并统计数量
    for item in reduces:
        category = item['task_type']
        grouped[category] += 1
    mapping_type = dict(grouped)

    for index, item_number in enumerate(
            [recommend_number - (
                    mapping_type[
                        PostAnswers.task_type_推荐回答] if PostAnswers.task_type_推荐回答 in mapping_type else 0),
             good_at_number - (
                     mapping_type[
                         PostAnswers.task_type_擅长回答] if PostAnswers.task_type_擅长回答 in mapping_type else 0),
             invited_number - (
                     mapping_type[
                         PostAnswers.task_type_邀请回答] if PostAnswers.task_type_邀请回答 in mapping_type else 0),
             message_invitation_number - (mapping_type[
                 PostAnswersMessageInvitation.task_type] if PostAnswersMessageInvitation.task_type in mapping_type else 0),
             new_number - (mapping_type[
                 PostAnswers.task_type_最新问题回答] if PostAnswers.task_type_最新问题回答 in mapping_type else 0),
             mcn_number - (
                     mapping_type[
                         PostAnswers.task_type_种草回答] if PostAnswers.task_type_种草回答 in mapping_type else 0),
             draft_good_at_number - (
                     mapping_type[
                         PostAnswers.task_type_草稿回答] if PostAnswers.task_type_草稿回答 in mapping_type else 0),
             article_number - (
                     mapping_type[PublishArticle.task_type] if PublishArticle.task_type in mapping_type else 0),
             draft_article_number - (
                     mapping_type[
                         PublishArticle.task_type_草稿] if PublishArticle.task_type_草稿 in mapping_type else 0),
             ideas_number - (mapping_type[PublishIdeas.task_type] if PublishIdeas.task_type in mapping_type else 0),
             asking_questions_number - (
                     mapping_type[AskingQuestions.task_type] if AskingQuestions.task_type in mapping_type else 0),
             follow_number - (mapping_type[Follow.task_type] if Follow.task_type in mapping_type else 0),
             follow_recommend_number - (
                     mapping_type[FollowRecommend.task_type] if FollowRecommend.task_type in mapping_type else 0),
             refresh_likes_number - (
                     mapping_type[RefreshLikes.task_type] if RefreshLikes.task_type in mapping_type else 0),
             random_browsing_number - (
                     mapping_type[RandomBrowsing.task_type] if RandomBrowsing.task_type in mapping_type else 0)]):
        data_list = []
        for i in range(item_number):
            data = {
                'account_id': account['id'],
                "task_type": index + 1,
                "command": command,
                "priority": random.randint(0, 1000000),
                "status": 1,
                'plan_date': datetime.date.today(),
                'finish_time': datetime.datetime(2000, 1, 1, 0, 0, 0),
                'create_time': datetime.datetime.now()
            }
            data_list.append(data)

        pool = await create_pool(db='zhihu')
        try:
            await insert_batch(pool=pool, table_name='task_plan', data_list=data_list)
        finally:
            await close_pool(pool)


# 生成所有账号任务
async def generate_plans(accounts, task_setting_list_mapping, is_reset=False):
    # 1.如果今日已经生成计划，则跳过
    # 2.如果重置，则删除之前的未完成任务，重新下发任务。
    for account in accounts:
        await generate_plan(account=account, task_setting_list=task_setting_list_mapping[account['id']],
                            is_reset=is_reset)


async def start_one_task(account, accounts, task_plan, hide: bool):
    # 创建数据库连接池
    pool = await create_pool(db='zhihu')
    html_lock: Lock = asyncio.Lock()
    resource_lock: Lock = asyncio.Lock()
    try:
        async def run_task(account, task_plan):
            if task_plan['task_type'] == PostAnswers.task_type_推荐回答:
                await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
                logging.info(f"[{account['account_name']}]开始执行推荐回答任务")
                # 推荐回答
                operation = PostAnswers(pool=pool, html_lock=html_lock, command=task_plan['command'],
                                        account_username=account['username'],
                                        account_name=account['account_name'],
                                        user_data_dir_path=account['user_data_dir_path'],
                                        remote_debugging_port=account['remote_debugging_port'],
                                        browser_type=account['browser_type'], hide=hide, label="为你推荐",
                                        draft=False)
                # 初始化资源管理器
                operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                              accounts=accounts, folder_path=pictures_file_path)
                response: dict = await operation.run()
                task_plan['finish_time'] = datetime.datetime.now()
                if response:
                    task_plan['status'] = 2 if response['code'] else 3
                    task_plan['message'] = response['message']
                else:
                    task_plan['status'] = 0
                    task_plan['message'] = "执行结果为None"
                await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
            elif task_plan['task_type'] == PostAnswers.task_type_擅长回答:
                logging.info(f"[{account['account_name']}]开始执行擅长回答任务")
                # 擅长回答
                operation = PostAnswers(pool=pool, html_lock=html_lock, command=task_plan['command'],
                                        account_username=account['username'],
                                        account_name=account['account_name'],
                                        user_data_dir_path=account['user_data_dir_path'],
                                        remote_debugging_port=account[
                                            'remote_debugging_port'],
                                        browser_type=account['browser_type'],
                                        label="擅长话题", hide=hide, draft=False)
                # 初始化资源管理器
                operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                              accounts=accounts, folder_path=pictures_file_path)
                response: dict = await operation.run()
                task_plan['finish_time'] = datetime.datetime.now()
                if response:
                    task_plan['status'] = 2 if response['code'] else 3
                    task_plan['message'] = response['message']
                else:
                    task_plan['status'] = 0
                    task_plan['message'] = "执行结果为None"
                await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
            elif task_plan['task_type'] == PostAnswers.task_type_邀请回答:
                logging.info(f"[{account['account_name']}]开始执行邀请答任务")
                # 邀请回答
                operation = PostAnswers(pool=pool, html_lock=html_lock, command=task_plan['command'],
                                        account_username=account['username'],
                                        account_name=account['account_name'],
                                        user_data_dir_path=account['user_data_dir_path'],
                                        remote_debugging_port=account[
                                            'remote_debugging_port'],
                                        browser_type=account['browser_type'],
                                        label="邀请回答", hide=hide, draft=False)
                # 初始化资源管理器
                operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                              accounts=accounts, folder_path=pictures_file_path)
                response: dict = await operation.run()
                task_plan['finish_time'] = datetime.datetime.now()
                if response:
                    task_plan['status'] = 2 if response['code'] else 3
                    task_plan['message'] = response['message']
                else:
                    task_plan['status'] = 0
                    task_plan['message'] = "执行结果为None"
                await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
            elif task_plan['task_type'] == PostAnswersMessageInvitation.task_type:
                logging.info(f"[{account['account_name']}]开始执行消息邀请回答任务")
                # 消息邀请回答
                operation = PostAnswersMessageInvitation(pool=pool, html_lock=html_lock,
                                                         command=task_plan['command'],
                                                         account_username=account['username'],
                                                         account_name=account['account_name'],
                                                         user_data_dir_path=account['user_data_dir_path'],
                                                         remote_debugging_port=account[
                                                             'remote_debugging_port'],
                                                         browser_type=account['browser_type'], hide=hide)
                # 初始化资源管理器
                operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                              accounts=accounts, folder_path=pictures_file_path)
                response: dict = await operation.run()
                task_plan['finish_time'] = datetime.datetime.now()
                if response:
                    task_plan['status'] = 2 if response['code'] else 3
                    task_plan['message'] = response['message']
                else:
                    task_plan['status'] = 0
                    task_plan['message'] = "执行结果为None"
                await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
            elif task_plan['task_type'] == PostAnswers.task_type_最新问题回答:
                logging.info(f"[{account['account_name']}]开始执行最新问题回答任务")
                # 最新问题回答
                operation = PostAnswers(pool=pool, html_lock=html_lock, command=task_plan['command'],
                                        account_username=account['username'],
                                        account_name=account['account_name'],
                                        user_data_dir_path=account['user_data_dir_path'],
                                        remote_debugging_port=account[
                                            'remote_debugging_port'],
                                        browser_type=account['browser_type'],
                                        label="最新问题", hide=hide, draft=False)
                # 初始化资源管理器
                operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                              accounts=accounts, folder_path=pictures_file_path)
                response: dict = await operation.run()
                task_plan['finish_time'] = datetime.datetime.now()
                if response:
                    task_plan['status'] = 2 if response['code'] else 3
                    task_plan['message'] = response['message']
                else:
                    task_plan['status'] = 0
                    task_plan['message'] = "执行结果为None"
                await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
            elif task_plan['task_type'] == PostAnswers.task_type_种草回答:
                logging.info(f"[{account['account_name']}]开始执行种草回答任务")
                # 种草回答
                operation = PostAnswers(pool=pool, html_lock=html_lock, command=task_plan['command'],
                                        account_username=account['username'],
                                        account_name=account['account_name'],
                                        user_data_dir_path=account['user_data_dir_path'],
                                        remote_debugging_port=account[
                                            'remote_debugging_port'],
                                        browser_type=account['browser_type'],
                                        label="种草回答", hide=hide, draft=False)
                # 初始化资源管理器
                operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                              accounts=accounts, folder_path=pictures_file_path)
                response: dict = await operation.run()
                task_plan['finish_time'] = datetime.datetime.now()
                if response:
                    task_plan['status'] = 2 if response['code'] else 3
                    task_plan['message'] = response['message']
                else:
                    task_plan['status'] = 0
                    task_plan['message'] = "执行结果为None"
                await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
            elif task_plan['task_type'] == PostAnswers.task_type_草稿回答:
                logging.info(f"[{account['account_name']}]开始执行草稿回答任务")
                # 草稿回答
                operation = PostAnswers(pool=pool, html_lock=html_lock, command=task_plan['command'],
                                        account_username=account['username'],
                                        account_name=account['account_name'],
                                        user_data_dir_path=account['user_data_dir_path'],
                                        remote_debugging_port=account[
                                            'remote_debugging_port'],
                                        browser_type=account['browser_type'],
                                        label="擅长话题", hide=hide, draft=True)
                # 初始化资源管理器
                operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                              accounts=accounts, folder_path=pictures_file_path)
                response: dict = await operation.run()
                task_plan['finish_time'] = datetime.datetime.now()
                if response:
                    task_plan['status'] = 2 if response['code'] else 3
                    task_plan['message'] = response['message']
                else:
                    task_plan['status'] = 0
                    task_plan['message'] = "执行结果为None"
                await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
            elif task_plan['task_type'] == PublishArticle.task_type:
                logging.info(f"[{account['account_name']}]开始执行发布文章任务")
                # 发布文章
                operation = PublishArticle(pool=pool, html_lock=html_lock,
                                           command=task_plan['command'],
                                           account_username=account['username'],
                                           account_name=account['account_name'],
                                           user_data_dir_path=account['user_data_dir_path'],
                                           remote_debugging_port=account['remote_debugging_port'],
                                           browser_type=account['browser_type'],
                                           draft=False, hide=hide)
                # 初始化资源管理器
                operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                              accounts=accounts, folder_path=pictures_file_path)
                response: dict = await operation.run()
                task_plan['finish_time'] = datetime.datetime.now()
                if response:
                    task_plan['status'] = 2 if response['code'] else 3
                    task_plan['message'] = response['message']
                else:
                    task_plan['status'] = 0
                    task_plan['message'] = "执行结果为None"
                await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
            elif task_plan['task_type'] == PublishArticle.task_type_草稿:
                logging.info(f"[{account['account_name']}]开始执行草稿文章任务")
                # 草稿文章
                operation = PublishArticle(pool=pool, html_lock=html_lock,
                                           command=task_plan['command'],
                                           account_username=account['username'],
                                           account_name=account['account_name'],
                                           user_data_dir_path=account['user_data_dir_path'],
                                           remote_debugging_port=account['remote_debugging_port'],
                                           browser_type=account['browser_type'],
                                           draft=True, hide=hide)
                # 初始化资源管理器
                operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                              accounts=accounts, folder_path=pictures_file_path)
                response: dict = await operation.run()
                task_plan['finish_time'] = datetime.datetime.now()
                if response:
                    task_plan['status'] = 2 if response['code'] else 3
                    task_plan['message'] = response['message']
                else:
                    task_plan['status'] = 0
                    task_plan['message'] = "执行结果为None"
                await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
            elif task_plan['task_type'] == PublishIdeas.task_type:
                logging.info(f"[{account['account_name']}]开始执行发布想法任务")
                # 发布想法
                operation = PublishIdeas(pool=pool, html_lock=html_lock,
                                         command=task_plan['command'],
                                         account_username=account['username'],
                                         account_name=account['account_name'],
                                         user_data_dir_path=account['user_data_dir_path'],
                                         remote_debugging_port=account['remote_debugging_port'],
                                         browser_type=account['browser_type'], hide=hide)
                # 初始化资源管理器
                operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                              accounts=accounts, folder_path=pictures_file_path)
                response: dict = await operation.run()
                task_plan['finish_time'] = datetime.datetime.now()
                if response:
                    task_plan['status'] = 2 if response['code'] else 3
                    task_plan['message'] = response['message']
                else:
                    task_plan['status'] = 0
                    task_plan['message'] = "执行结果为None"
                await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
            elif task_plan['task_type'] == AskingQuestions.task_type:
                logging.info(f"[{account['account_name']}]开始执行发布提问任务")
                # 发布提问
                operation = AskingQuestions(pool=pool, html_lock=html_lock,
                                            command=task_plan['command'],
                                            account_username=account['username'],
                                            account_name=account['account_name'],
                                            user_data_dir_path=account['user_data_dir_path'],
                                            remote_debugging_port=account['remote_debugging_port'],
                                            browser_type=account['browser_type'], hide=hide)
                # 初始化资源管理器
                operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                              accounts=accounts, folder_path=pictures_file_path)
                response: dict = await operation.run()
                task_plan['finish_time'] = datetime.datetime.now()
                if response:
                    task_plan['status'] = 2 if response['code'] else 3
                    task_plan['message'] = response['message']
                else:
                    task_plan['status'] = 0
                    task_plan['message'] = "执行结果为None"
                await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
            elif task_plan['task_type'] == Follow.task_type:
                logging.info(f"[{account['account_name']}]开始执行任务关注任务")
                # 任务关注(一天只能执行一次)
                operation = Follow(pool=pool, html_lock=html_lock, command=task_plan['command'],
                                   account_username=account['username'],
                                   account_name=account['account_name'],
                                   user_data_dir_path=account['user_data_dir_path'],
                                   remote_debugging_port=account['remote_debugging_port'],
                                   browser_type=account['browser_type'], hide=hide)
                # 初始化资源管理器
                operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                              accounts=accounts, folder_path=pictures_file_path)
                response: dict = await operation.run()
                task_plan['finish_time'] = datetime.datetime.now()
                if response:
                    task_plan['status'] = 2 if response['code'] else 3
                    task_plan['message'] = response['message']
                else:
                    task_plan['status'] = 0
                    task_plan['message'] = "执行结果为None"
                await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
            elif task_plan['task_type'] == FollowRecommend.task_type:
                logging.info(f"[{account['account_name']}]开始执行推荐关注任务")
                # 推荐关注
                operation = FollowRecommend(pool=pool, html_lock=html_lock,
                                            command=task_plan['command'],
                                            account_username=account['username'],
                                            account_name=account['account_name'],
                                            user_data_dir_path=account['user_data_dir_path'],
                                            remote_debugging_port=account['remote_debugging_port'],
                                            browser_type=account['browser_type'], hide=hide)
                # 初始化资源管理器
                operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                              accounts=accounts, folder_path=pictures_file_path)
                response: dict = await operation.run()
                task_plan['finish_time'] = datetime.datetime.now()
                if response:
                    task_plan['status'] = 2 if response['code'] else 3
                    task_plan['message'] = response['message']
                else:
                    task_plan['status'] = 0
                    task_plan['message'] = "执行结果为None"
                await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
            elif task_plan['task_type'] == RefreshLikes.task_type:
                logging.info(f"[{account['account_name']}]开始执行互赞任务")
                # 互赞
                operation = RefreshLikes(pool=pool, html_lock=html_lock, command=task_plan['command'],
                                         account_username=account['username'],
                                         account_name=account['account_name'],
                                         user_data_dir_path=account['user_data_dir_path'],
                                         remote_debugging_port=account['remote_debugging_port'],
                                         browser_type=account['browser_type'], hide=hide, home_urls=[])  # TODO
                # 初始化资源管理器
                operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                              accounts=accounts, folder_path=pictures_file_path)
                response: dict = await operation.run()
                task_plan['finish_time'] = datetime.datetime.now()
                if response:
                    task_plan['status'] = 2 if response['code'] else 3
                    task_plan['message'] = response['message']
                else:
                    task_plan['status'] = 0
                    task_plan['message'] = "执行结果为None"
                await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
            elif task_plan['task_type'] == RandomBrowsing.task_type:
                logging.info(f"[{account['account_name']}]开始执行漫游任务")
                # 漫游
                operation = RandomBrowsing(pool=pool, html_lock=html_lock,
                                           command=task_plan['command'],
                                           account_username=account['username'],
                                           account_name=account['account_name'],
                                           user_data_dir_path=account['user_data_dir_path'],
                                           remote_debugging_port=account['remote_debugging_port'],
                                           browser_type=account['browser_type'], hide=hide)
                # 初始化资源管理器
                operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                              accounts=accounts, folder_path=pictures_file_path)
                response: dict = await operation.run()
                task_plan['finish_time'] = datetime.datetime.now()
                if response:
                    task_plan['status'] = 2 if response['code'] else 3
                    task_plan['message'] = response['message']
                else:
                    task_plan['status'] = 0
                    task_plan['message'] = "执行结果为None"
                await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
            else:
                pass

        # 执行任务
        await run_task(account, task_plan)
    except:
        traceback.print_exc()
        error = traceback.format_exc()
    finally:
        await close_pool(pool)
    # 关闭浏览器应用
    kill_process_by_name("chrome.exe")
    kill_process_by_name("msedge.exe")


async def start_all_task(hide: bool):
    # 获取当前文件的绝对路径
    current_file_path = os.path.abspath(__file__)
    # 获取当前文件所在的目录
    current_directory = os.path.dirname(current_file_path)
    # 构建CSS文件的完整路径
    pictures_file_path = os.path.join(current_directory, "pictures")

    # 创建数据库连接池
    pool = await create_pool(db='zhihu')
    html_lock: Lock = asyncio.Lock()
    resource_lock: Lock = asyncio.Lock()
    try:
        async def run_task(account):
            while True:
                task_plans = await select_list(pool=pool, table_name='task_plan',
                                               condition=[
                                                   {'field': 'account_id', 'value': account['id'], 'op': 'ct'},
                                                   {'field': 'plan_date',
                                                    'value': datetime.date.today().strftime("%Y-%m-%d"), 'op': 'eq'},
                                                   {'field': 'status', 'value': 1, 'op': 'eq'},
                                               ],
                                               order_by=[{'field': 'priority', 'value': 'desc'}])
                if len(task_plans) == 0:
                    logging.info(f"[{account['account_name']}]没有任务了")
                    logging.info(f"[{account['account_name']}]没有任务了，没有任务则执行漫游")
                    # 没有任务则执行漫游
                    # 漫游
                    if 'command' in account.keys() and \
                            account['command'] is not None and \
                            account['command'].strip() != '':
                        operation = RandomBrowsing(pool=pool, html_lock=html_lock,
                                                   command=account['command'],
                                                   account_username=account['username'],
                                                   account_name=account['account_name'],
                                                   user_data_dir_path=account['user_data_dir_path'],
                                                   remote_debugging_port=account['remote_debugging_port'],
                                                   browser_type=account['browser_type'], hide=hide, duration=60 * 60)
                        # 初始化资源管理器
                        operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                                      accounts=accounts, folder_path=pictures_file_path)
                        response: dict = await operation.run()
                    continue
                    # break
                else:
                    task_plan = task_plans[0]
                    if task_plan['task_type'] == PostAnswers.task_type_推荐回答:
                        logging.info(f"[{account['account_name']}]开始执行推荐回答任务")
                        # 推荐回答
                        operation = PostAnswers(pool=pool, html_lock=html_lock, command=task_plan['command'],
                                                account_username=account['username'],
                                                account_name=account['account_name'],
                                                user_data_dir_path=account['user_data_dir_path'],
                                                remote_debugging_port=account['remote_debugging_port'],
                                                browser_type=account['browser_type'], hide=hide, label="为你推荐",
                                                draft=False)
                        # 初始化资源管理器
                        operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                                      accounts=accounts, folder_path=pictures_file_path)
                        response: dict = await operation.run()
                        task_plan['finish_time'] = datetime.datetime.now()
                        if response:
                            task_plan['status'] = 2 if response['code'] else 3
                            task_plan['message'] = response['message']
                        else:
                            task_plan['status'] = 0
                            task_plan['message'] = "执行结果为None"
                        await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
                        continue
                    elif task_plan['task_type'] == PostAnswers.task_type_擅长回答:
                        logging.info(f"[{account['account_name']}]开始执行擅长回答任务")
                        # 擅长回答
                        operation = PostAnswers(pool=pool, html_lock=html_lock, command=task_plan['command'],
                                                account_username=account['username'],
                                                account_name=account['account_name'],
                                                user_data_dir_path=account['user_data_dir_path'],
                                                remote_debugging_port=account[
                                                    'remote_debugging_port'],
                                                browser_type=account['browser_type'],
                                                label="擅长话题", hide=hide, draft=False)
                        # 初始化资源管理器
                        operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                                      accounts=accounts, folder_path=pictures_file_path)
                        response: dict = await operation.run()
                        task_plan['finish_time'] = datetime.datetime.now()
                        if response:
                            task_plan['status'] = 2 if response['code'] else 3
                            task_plan['message'] = response['message']
                        else:
                            task_plan['status'] = 0
                            task_plan['message'] = "执行结果为None"
                        await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
                        continue
                    elif task_plan['task_type'] == PostAnswers.task_type_邀请回答:
                        logging.info(f"[{account['account_name']}]开始执行邀请答任务")
                        # 邀请回答
                        operation = PostAnswers(pool=pool, html_lock=html_lock, command=task_plan['command'],
                                                account_username=account['username'],
                                                account_name=account['account_name'],
                                                user_data_dir_path=account['user_data_dir_path'],
                                                remote_debugging_port=account[
                                                    'remote_debugging_port'],
                                                browser_type=account['browser_type'],
                                                label="邀请回答", hide=hide, draft=False)
                        # 初始化资源管理器
                        operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                                      accounts=accounts, folder_path=pictures_file_path)
                        response: dict = await operation.run()
                        task_plan['finish_time'] = datetime.datetime.now()
                        if response:
                            task_plan['status'] = 2 if response['code'] else 3
                            task_plan['message'] = response['message']
                        else:
                            task_plan['status'] = 0
                            task_plan['message'] = "执行结果为None"
                        await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
                        continue
                    elif task_plan['task_type'] == PostAnswersMessageInvitation.task_type:
                        logging.info(f"[{account['account_name']}]开始执行消息邀请回答任务")
                        # 消息邀请回答
                        operation = PostAnswersMessageInvitation(pool=pool, html_lock=html_lock,
                                                                 command=task_plan['command'],
                                                                 account_username=account['username'],
                                                                 account_name=account['account_name'],
                                                                 user_data_dir_path=account['user_data_dir_path'],
                                                                 remote_debugging_port=account[
                                                                     'remote_debugging_port'],
                                                                 browser_type=account['browser_type'], hide=hide)
                        # 初始化资源管理器
                        operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                                      accounts=accounts, folder_path=pictures_file_path)
                        response: dict = await operation.run()
                        task_plan['finish_time'] = datetime.datetime.now()
                        if response:
                            task_plan['status'] = 2 if response['code'] else 3
                            task_plan['message'] = response['message']
                        else:
                            task_plan['status'] = 0
                            task_plan['message'] = "执行结果为None"
                        await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
                        continue
                    elif task_plan['task_type'] == PostAnswers.task_type_最新问题回答:
                        logging.info(f"[{account['account_name']}]开始执行最新问题回答任务")
                        # 最新问题回答
                        operation = PostAnswers(pool=pool, html_lock=html_lock, command=task_plan['command'],
                                                account_username=account['username'],
                                                account_name=account['account_name'],
                                                user_data_dir_path=account['user_data_dir_path'],
                                                remote_debugging_port=account[
                                                    'remote_debugging_port'],
                                                browser_type=account['browser_type'],
                                                label="最新问题", hide=hide, draft=False)
                        # 初始化资源管理器
                        operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                                      accounts=accounts, folder_path=pictures_file_path)
                        response: dict = await operation.run()
                        task_plan['finish_time'] = datetime.datetime.now()
                        if response:
                            task_plan['status'] = 2 if response['code'] else 3
                            task_plan['message'] = response['message']
                        else:
                            task_plan['status'] = 0
                            task_plan['message'] = "执行结果为None"
                        await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
                        continue
                    elif task_plan['task_type'] == PostAnswers.task_type_种草回答:
                        logging.info(f"[{account['account_name']}]开始执行种草回答任务")
                        # 种草回答
                        operation = PostAnswers(pool=pool, html_lock=html_lock, command=task_plan['command'],
                                                account_username=account['username'],
                                                account_name=account['account_name'],
                                                user_data_dir_path=account['user_data_dir_path'],
                                                remote_debugging_port=account[
                                                    'remote_debugging_port'],
                                                browser_type=account['browser_type'],
                                                label="种草回答", hide=hide, draft=False)
                        # 初始化资源管理器
                        operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                                      accounts=accounts, folder_path=pictures_file_path)
                        response: dict = await operation.run()
                        task_plan['finish_time'] = datetime.datetime.now()
                        if response:
                            task_plan['status'] = 2 if response['code'] else 3
                            task_plan['message'] = response['message']
                        else:
                            task_plan['status'] = 0
                            task_plan['message'] = "执行结果为None"
                        await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
                        continue
                    elif task_plan['task_type'] == PostAnswers.task_type_草稿回答:
                        logging.info(f"[{account['account_name']}]开始执行草稿回答任务")
                        # 草稿回答
                        operation = PostAnswers(pool=pool, html_lock=html_lock, command=task_plan['command'],
                                                account_username=account['username'],
                                                account_name=account['account_name'],
                                                user_data_dir_path=account['user_data_dir_path'],
                                                remote_debugging_port=account[
                                                    'remote_debugging_port'],
                                                browser_type=account['browser_type'],
                                                label="擅长话题", hide=hide, draft=True)
                        # 初始化资源管理器
                        operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                                      accounts=accounts, folder_path=pictures_file_path)
                        response: dict = await operation.run()
                        task_plan['finish_time'] = datetime.datetime.now()
                        if response:
                            task_plan['status'] = 2 if response['code'] else 3
                            task_plan['message'] = response['message']
                        else:
                            task_plan['status'] = 0
                            task_plan['message'] = "执行结果为None"
                        await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
                        continue
                    elif task_plan['task_type'] == PublishArticle.task_type:
                        logging.info(f"[{account['account_name']}]开始执行发布文章任务")
                        # 发布文章
                        operation = PublishArticle(pool=pool, html_lock=html_lock,
                                                   command=task_plan['command'],
                                                   account_username=account['username'],
                                                   account_name=account['account_name'],
                                                   user_data_dir_path=account['user_data_dir_path'],
                                                   remote_debugging_port=account['remote_debugging_port'],
                                                   browser_type=account['browser_type'],
                                                   draft=False, hide=hide)
                        # 初始化资源管理器
                        operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                                      accounts=accounts, folder_path=pictures_file_path)
                        response: dict = await operation.run()
                        task_plan['finish_time'] = datetime.datetime.now()
                        if response:
                            task_plan['status'] = 2 if response['code'] else 3
                            task_plan['message'] = response['message']
                        else:
                            task_plan['status'] = 0
                            task_plan['message'] = "执行结果为None"
                        await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
                        continue
                    elif task_plan['task_type'] == PublishArticle.task_type_草稿:
                        logging.info(f"[{account['account_name']}]开始执行草稿文章任务")
                        # 草稿文章
                        operation = PublishArticle(pool=pool, html_lock=html_lock,
                                                   command=task_plan['command'],
                                                   account_username=account['username'],
                                                   account_name=account['account_name'],
                                                   user_data_dir_path=account['user_data_dir_path'],
                                                   remote_debugging_port=account['remote_debugging_port'],
                                                   browser_type=account['browser_type'],
                                                   draft=True, hide=hide)
                        # 初始化资源管理器
                        operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                                      accounts=accounts, folder_path=pictures_file_path)
                        response: dict = await operation.run()
                        task_plan['finish_time'] = datetime.datetime.now()
                        if response:
                            task_plan['status'] = 2 if response['code'] else 3
                            task_plan['message'] = response['message']
                        else:
                            task_plan['status'] = 0
                            task_plan['message'] = "执行结果为None"
                        await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
                        continue
                    elif task_plan['task_type'] == PublishIdeas.task_type:
                        logging.info(f"[{account['account_name']}]开始执行发布想法任务")
                        # 发布想法
                        operation = PublishIdeas(pool=pool, html_lock=html_lock,
                                                 command=task_plan['command'],
                                                 account_username=account['username'],
                                                 account_name=account['account_name'],
                                                 user_data_dir_path=account['user_data_dir_path'],
                                                 remote_debugging_port=account['remote_debugging_port'],
                                                 browser_type=account['browser_type'], hide=hide)
                        # 初始化资源管理器
                        operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                                      accounts=accounts, folder_path=pictures_file_path)
                        response: dict = await operation.run()
                        task_plan['finish_time'] = datetime.datetime.now()
                        if response:
                            task_plan['status'] = 2 if response['code'] else 3
                            task_plan['message'] = response['message']
                        else:
                            task_plan['status'] = 0
                            task_plan['message'] = "执行结果为None"
                        await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
                        continue
                    elif task_plan['task_type'] == AskingQuestions.task_type:
                        logging.info(f"[{account['account_name']}]开始执行发布提问任务")
                        # 发布提问
                        operation = AskingQuestions(pool=pool, html_lock=html_lock,
                                                    command=task_plan['command'],
                                                    account_username=account['username'],
                                                    account_name=account['account_name'],
                                                    user_data_dir_path=account['user_data_dir_path'],
                                                    remote_debugging_port=account['remote_debugging_port'],
                                                    browser_type=account['browser_type'], hide=hide)
                        # 初始化资源管理器
                        operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                                      accounts=accounts, folder_path=pictures_file_path)
                        response: dict = await operation.run()
                        task_plan['finish_time'] = datetime.datetime.now()
                        if response:
                            task_plan['status'] = 2 if response['code'] else 3
                            task_plan['message'] = response['message']
                        else:
                            task_plan['status'] = 0
                            task_plan['message'] = "执行结果为None"
                        await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
                        continue
                    elif task_plan['task_type'] == Follow.task_type:
                        logging.info(f"[{account['account_name']}]开始执行任务关注任务")
                        # 任务关注(一天只能执行一次)
                        operation = Follow(pool=pool, html_lock=html_lock, command=task_plan['command'],
                                           account_username=account['username'],
                                           account_name=account['account_name'],
                                           user_data_dir_path=account['user_data_dir_path'],
                                           remote_debugging_port=account['remote_debugging_port'],
                                           browser_type=account['browser_type'], hide=hide)
                        # 初始化资源管理器
                        operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                                      accounts=accounts, folder_path=pictures_file_path)
                        response: dict = await operation.run()
                        task_plan['finish_time'] = datetime.datetime.now()
                        if response:
                            task_plan['status'] = 2 if response['code'] else 3
                            task_plan['message'] = response['message']
                        else:
                            task_plan['status'] = 0
                            task_plan['message'] = "执行结果为None"
                        await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
                        continue
                    elif task_plan['task_type'] == FollowRecommend.task_type:
                        logging.info(f"[{account['account_name']}]开始执行推荐关注任务")
                        # 推荐关注
                        operation = FollowRecommend(pool=pool, html_lock=html_lock,
                                                    command=task_plan['command'],
                                                    account_username=account['username'],
                                                    account_name=account['account_name'],
                                                    user_data_dir_path=account['user_data_dir_path'],
                                                    remote_debugging_port=account['remote_debugging_port'],
                                                    browser_type=account['browser_type'], hide=hide)
                        # 初始化资源管理器
                        operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                                      accounts=accounts, folder_path=pictures_file_path)
                        response: dict = await operation.run()
                        task_plan['finish_time'] = datetime.datetime.now()
                        if response:
                            task_plan['status'] = 2 if response['code'] else 3
                            task_plan['message'] = response['message']
                        else:
                            task_plan['status'] = 0
                            task_plan['message'] = "执行结果为None"
                        await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
                        continue
                    elif task_plan['task_type'] == RefreshLikes.task_type:
                        logging.info(f"[{account['account_name']}]开始执行互赞任务")
                        # 互赞
                        operation = RefreshLikes(pool=pool, html_lock=html_lock, command=task_plan['command'],
                                                 account_username=account['username'],
                                                 account_name=account['account_name'],
                                                 user_data_dir_path=account['user_data_dir_path'],
                                                 remote_debugging_port=account['remote_debugging_port'],
                                                 browser_type=account['browser_type'], hide=hide, home_urls=[])  # TODO
                        # 初始化资源管理器
                        operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                                      accounts=accounts, folder_path=pictures_file_path)
                        response: dict = await operation.run()
                        task_plan['finish_time'] = datetime.datetime.now()
                        if response:
                            task_plan['status'] = 2 if response['code'] else 3
                            task_plan['message'] = response['message']
                        else:
                            task_plan['status'] = 0
                            task_plan['message'] = "执行结果为None"
                        await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
                        continue
                    elif task_plan['task_type'] == RandomBrowsing.task_type:
                        logging.info(f"[{account['account_name']}]开始执行漫游任务")
                        # 漫游
                        operation = RandomBrowsing(pool=pool, html_lock=html_lock,
                                                   command=task_plan['command'],
                                                   account_username=account['username'],
                                                   account_name=account['account_name'],
                                                   user_data_dir_path=account['user_data_dir_path'],
                                                   remote_debugging_port=account['remote_debugging_port'],
                                                   browser_type=account['browser_type'], hide=hide)
                        # 初始化资源管理器
                        operation.resourcesService = ResourcesService(pool=pool, resource_lock=resource_lock,
                                                                      accounts=accounts, folder_path=pictures_file_path)
                        response: dict = await operation.run()
                        task_plan['finish_time'] = datetime.datetime.now()
                        if response:
                            task_plan['status'] = 2 if response['code'] else 3
                            task_plan['message'] = response['message']
                        else:
                            task_plan['status'] = 0
                            task_plan['message'] = "执行结果为None"
                        await update_by_id(pool=pool, table_name='task_plan', data=task_plan)
                        continue
                    else:
                        pass

        async def run_spider():
            # 更新微博热点
            spider_wb = WeiboHotTopicSpider(pool=pool)
            await spider_wb.run()

            # 更新抖音热点
            spider_dy = DouyinHotTopicSpider(pool=pool)
            await spider_dy.run()

            # 图片爬虫
            spider_pixbay = PicturePixabaySpider(pool=pool, hide=hide)
            await spider_pixbay.run_with_no_end()

        pass
        # 查出账号信息
        accounts = select_list_by_database_table(database_name='zhihu', table_name='account',
                                                 conditions=[{'field': 'status', 'value': 1, 'op': 'eq'}])

        # python 11 新特性写法
        # # 创建任务组
        # async with asyncio.TaskGroup() as tg:
        #     for account in accounts:
        #         tg.create_task(run_task(account))
        #     # 开启一个图片爬虫
        #     tg.create_task(run_spider())
        # python 10 写法
        tasks = []
        for account in accounts:
            tasks.append(asyncio.create_task(run_task(account)))
        tasks.append(asyncio.create_task(run_spider()))

        await asyncio.gather(*tasks)
    except:
        traceback.print_exc()
        error = traceback.format_exc()
    finally:
        await close_pool(pool)
    # 关闭浏览器应用
    kill_process_by_name("chrome.exe")
    kill_process_by_name("msedge.exe")


if __name__ == '__main__':
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

    # 关闭浏览器应用
    kill_process_by_name("chrome.exe")
    asyncio.run(start_all_task(hide=False))
