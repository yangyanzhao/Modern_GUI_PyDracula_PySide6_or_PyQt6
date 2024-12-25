"""
资源库-控制器
"""
import asyncio
import datetime
import logging
import os
import shutil
import subprocess
import traceback
from asyncio import Lock

import aiomysql

from gui.utils.file_lock import create_fold_path
from modules.zhihu_auto.chat.api import chat
from db.mysql.mysql_jdbc import create_pool


class ResourcesService:

    def __init__(self, pool, resource_lock: Lock, accounts: list, folder_path: str):
        # 多线程中的数据库连接池
        self.pool = pool
        self.resource_lock = resource_lock
        # 等待异步任务完成
        self.accounts = accounts
        self.folder_path = folder_path
        create_fold_path(fold_path=folder_path)
        files = os.listdir(folder_path)
        files_arr = ResourcesService.split_array(files, len(self.accounts))
        self.files_account = {}
        for i, account in enumerate(self.accounts):
            self.files_account[account['username']] = files_arr[i]

    @staticmethod
    def split_array(arr, N):
        """
        对数组进行等分
        """
        # 计算每个子数组的长度
        length = len(arr)
        split_size = length // N
        remainder = length % N

        result = []
        start = 0

        for i in range(N):
            if i < remainder:
                end = start + split_size + 1
            else:
                end = start + split_size
            result.append(arr[start:end])
            start = end

        return result

    async def get_three_pictures(self, account_username, account_name, type, pic_number: int = 3):
        """
        获取三张图片
        """
        async with self.resource_lock:
            # 获取文件夹中的所有文件
            files: list = self.files_account[account_username]
            if len(files) >= pic_number:
                selected_files = files
                files_dir_arr = [self.folder_path + "\\" + i for i in selected_files]
                return_files = []
                # 遍历
                for files_dir in files_dir_arr:
                    async with self.pool.acquire() as conn:
                        async with conn.cursor(aiomysql.DictCursor) as cur:
                            await cur.execute(
                                f'SELECT count(*) as `count` FROM used_pictures where files_dir="{files_dir}"')
                            count = await cur.fetchone()
                    if count['count'] == 0:
                        return_files.append(files_dir)
                        async with self.pool.acquire() as conn:
                            async with conn.cursor(aiomysql.DictCursor) as cur:
                                await cur.execute('''
                                    INSERT INTO used_pictures (account, `type`,files_dir,status,`date`,datetime) 
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                ''', (account_name, type, files_dir, 1, datetime.date.today(), datetime.datetime.now()))
                    else:
                        self.del_pictures([files_dir])
                    try:
                        if files_dir in files:
                            files.remove(files_dir)
                    except:
                        traceback.print_exc()
                        exc_info = traceback.format_exc()
                        pass
                    if len(return_files) >= pic_number:
                        break
                # 将图片移动到另一个文件夹
                return return_files

            else:
                # 图片不足啦
                logging.info(f"知乎图片不足啦-{datetime.datetime.now()}")
                pass

    async def del_pictures(self, picture_path_list: list):
        """
        删除图片【删除图片的动作，一定要在图片已经使用完毕之后再调用！！！】
        """
        if not picture_path_list:
            return
        try:
            for picture_path in picture_path_list:
                if picture_path and os.path.exists(picture_path):
                    # 删除文件
                    try:
                        os.remove(picture_path)
                    except:
                        try:
                            shutil.rmtree(picture_path)  # 对于目录
                        except OSError as e:
                            try:
                                os.unlink(picture_path)
                            except:
                                try:
                                    subprocess.check_call(['rm', '-f', picture_path])
                                except subprocess.CalledProcessError as e:
                                    logging.info(f"删除失败了: {e}")
        except Exception as e:
            traceback.print_exc()
            exc_info = traceback.format_exc()

    async def get_hot_topic(self):
        async with self.resource_lock:
            logging.info("获取话题名称")
            prompt = f"""
                                    # 角色
                                    你是一个具有极强的话题感知能力，具有敏锐的预见性和洞察力的思考者。
                                    # 约束
                                    - 使用中文回复。
                                    - 话题可以涉及所有领域，除了科技、政治事件和政治人物。
                                    - 不要涉及政治事件和政治人物。
                                    - 你要把自己当做一个真人，绝对不能暴露出你是AI,你自己更不能提及自己是AI。
                                    - 回答要言简意赅，限制在20个字以内。
                                    """
            topic = None
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute('SELECT * FROM hot_topics where status=0 ORDER BY id desc limit 1')
                    rows = await cur.fetchall()
                    topic = rows[0]['topic_name']
            if topic is None:
                logging.info(f"抖音热点话题不足啦-{datetime.datetime.now()}")
                question = f"请随机给我一个话题，要求限制在20个字以内。"
            else:
                question = f"给我一个关于'{topic}'的话题，要求限制在20个字以内。"
            logging.info(f"请求GPT改写话题名称：{topic}")
            result, m = await chat(self.pool, prompt, question)
            logging.info(f"GPT修正话题名称为：{result}")
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute('''
                        UPDATE hot_topics SET status = 1 WHERE topic_name = %s
                    ''', (topic,))
            if result is None:
                result = topic
            return result

    async def get_question(self):
        async with self.resource_lock:
            """
            获取一个问题
            """
            topic = None
            prompt = None
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute('SELECT * FROM asking_questions')
                    rows = await cur.fetchall()
                    questions_all = rows
                    qs = [q['question'] for q in questions_all]
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute('SELECT * FROM hot_topics where status=0 ORDER BY id desc limit 1')
                    rows = await cur.fetchall()
                    hot_topics_one = rows
            if len(list(hot_topics_one)) == 0:
                logging.error("热点话题不足")
                return None
            topic = hot_topics_one[0]['topic_name']
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute('''
                        UPDATE hot_topics SET status = 1 WHERE topic_name = %s
                    ''', (topic,))
            prompt = f"""
                                            你好，我是一个充满好奇心的用户，喜欢探索各种有趣的话题。让我们开始吧！
                                            规则：
                                            1. 直接给出问题本身，不要啰嗦，错误示范：'你好，好奇心旺盛的探索者！既然你让我问你一个问题，那么我来问一个：如果你有机会选择一个超能力，你会选择什么，并且你打算如何使用这个超能力呢？'。正确示范：'如果你有机会选择一个超能力，你会选择什么，并且你打算如何使用这个超能力呢？'
                                            2. 问题要千奇百怪，天马行空，自由想象，自由组合，奇闻趣事。
                                            3. 用中文回答.
                                            4. 回答不要与以下数组中的任何一个雷同{qs}
                                            5. 回答以问号结尾。
                                            6. 回答内容要在45个字以内。
                                            """
            question = f"关于'{topic}'，请你问我一个问题,"
            result, m = await chat(self.pool, prompt, question)
            return result, topic


async def start():
    pool = await create_pool(db='zhihu')
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute('SELECT * FROM account where status=1')
            rows: list[dict] = await cur.fetchall()
            accounts = rows
    service = ResourcesService(pool=pool, accounts=accounts)
    question, topic = await service.get_question()
    print(question, topic)


if __name__ == '__main__':
    # 创建日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logs_dir = fr'logs\{datetime.date.today()}'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    # 创建文件处理器，将日志写入文件
    file_handler = logging.FileHandler(
        filename=os.path.join(logs_dir, f'resources_service_{datetime.date.today()}.log'),
        mode='a',
        encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    # 创建控制台处理器，将日志输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    # 将处理器添加到日志记录器
    logger.addHandler(file_handler)

    asyncio.run(start())
