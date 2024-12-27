"""
秘塔【特长：超强检索超长输出】
功能一：对话
"""
import asyncio
import datetime
import json
import traceback

import aiohttp
import requests

from db.mysql.mysql_jdbc import insert, create_pool, close_pool


URL = "http://124.222.40.17:8004/v1/chat/completions"
URL_CHECK = "http://124.222.40.17:8004/token/check"

# 访问https://metaso.cn/界面F12从Cookie中找到uid和sid的值。将uid和sid拼接：uid-sid
UID = "66922f98d94bbd343a23a9b8"
SID = "2cd5d5fdf2764c4a8e3b600b3f877b9d"
token = f"{UID}-{SID}"


class MetasoAPIThree:

    @staticmethod
    async def chat(pool, prompt, question, timeout):

        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

        payload = json.dumps({
            # 全网model名称支持 -> 简洁：concise / 深入：detail / 研究：research
            # 学术model名称支持 -> 学术 - 简洁：concise - scholar / 学术 - 深入：detail - scholar / 学术 - 研究：research - scholar
            # model乱填的话，可以通过tempature参数来控制（但不支持学术）：简洁： < 0.4 / 深入： >= 0.4 & & < 0.7 / 研究： >= 0.7
            # model乱填的话，还可以通过消息内容包含指令来控制：↓↓↓
            # 简洁 -> 简洁搜索小米su7 / 深入 -> 深入搜索小米su7 / 研究 -> 研究搜索小米su7
            # 学术 - 简洁 -> 学术简洁搜索：小米su7 / 学术 - 深入 -> 学术深入搜索小米su7 / 学术研究 -> 学术研究搜索小米su7
            # 优先级：model > 消息内容指令 > tempature
            "model": "concise",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": question}
            ],
            # 如果使用SSE流请设置为true，默认false
            "stream": False
        })
        start_time = asyncio.get_event_loop().time()
        # 原始回答
        raw_answer = None
        # 处理后回答
        handle_answer = None
        # 状态
        status = None
        # 耗时
        elapsed_time = None
        # 报错信息
        error = None
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(URL, headers=headers, data=payload, timeout=timeout) as response:
                    if response.status == 200:
                        raw_answer = await response.text()
                        end_time = asyncio.get_event_loop().time()
                        elapsed_time = end_time - start_time
                        result: dict = json.loads(raw_answer)
                        if 'code' in result and result['code'] == -2001:
                            # 登录异常
                            # 1正常回答2超时3异常
                            status = 3
                            return None

                        choices = result['choices']
                        handle_answer = choices[0]['message']['content']
                        # 1正常回答2超时3异常
                        status = 1
                        return choices[0]['message']['content']
                    else:
                        raw_answer = await response.text()
                        end_time = asyncio.get_event_loop().time()
                        elapsed_time = end_time - start_time
                        status = 3
                        return None
            except asyncio.TimeoutError:
                end_time = asyncio.get_event_loop().time()
                elapsed_time = end_time - start_time
                status = 2
                return None
            except Exception as e:
                end_time = asyncio.get_event_loop().time()
                elapsed_time = end_time - start_time
                status = 3
                traceback.print_exc()
                error = traceback.format_exc()
            finally:
                # 这里要每一次的API访问进行记录
                data = {
                    "model": "MetasoAPIThree",
                    "prompt": prompt,
                    "question": None if question is None else question[:2000],
                    "raw_answer": None if raw_answer is None else raw_answer[:2000],
                    "handle_answer": None if handle_answer is None else handle_answer[:2000],
                    "status": status,  # 1正常2超时3异常
                    "elapsed_time": elapsed_time,
                    "error": error,
                    "date": datetime.date.today(),
                    "datetime": datetime.datetime.now()
                }
                await insert(pool=pool, table_name='chat_api_log', data=data)
    @staticmethod
    def token_check():
        """
        token校验有性
        """
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

        payload = json.dumps({
            "token": token
        })

        response = requests.request("POST", URL_CHECK, headers=headers, data=payload)
        print(response.text)
        return response.text
    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await MetasoAPIThree.chat(pool=pool, question=question, prompt=prompt, timeout=timeout)
            return result
        finally:
            await close_pool(pool)
