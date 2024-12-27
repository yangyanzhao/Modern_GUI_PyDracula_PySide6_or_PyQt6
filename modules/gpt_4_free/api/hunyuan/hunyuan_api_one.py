import asyncio
import datetime
import json
import re
import traceback
import uuid

import aiohttp

from db.mysql.mysql_jdbc import insert, create_pool, close_pool

"""
手机号码：15267398131
"""
# https://yuanbao.tencent.com/api/chat/8d9348da-b6b7-11ef-8392-8a8459414b6b 以uuid结尾的cookie
cookie = "_ga=GA1.2.51342098.1724403794; hy_source=web; _gcl_au=1.1.159388770.1733455914; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22100009122798%22%2C%22first_id%22%3A%221917e79bf0b1d3-0919c68c9b5b178-26001e51-2073600-1917e79bf0c1185%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkxN2U3OWJmMGIxZDMtMDkxOWM2OGM5YjViMTc4LTI2MDAxZTUxLTIwNzM2MDAtMTkxN2U3OWJmMGMxMTg1IiwiJGlkZW50aXR5X2xvZ2luX2lkIjoiMTAwMDA5MTIyNzk4In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22100009122798%22%7D%2C%22%24device_id%22%3A%221917e79bf0b1d3-0919c68c9b5b178-26001e51-2073600-1917e79bf0c1185%22%7D; hy_user=Ez0ij7vWOSGldwvF; hy_token=fSlnkD0y3cZj+vzJsyu5JBZ7ipUpXbdFLqVrBls3AQa3a02ZNQ6BKX88k6UfIBLl"


class HunYuanAPIOne:
    @staticmethod
    async def chat(pool, prompt, question, timeout):
        message = f"""
                system:
                {prompt}
                user:
                {question}
                assistant:
                """
        url = f"https://yuanbao.tencent.com/api/chat/{str(uuid.uuid4())}"

        payload = {'model': 'gpt_175B_0404', 'prompt': message, 'plugin': 'Adaptive', 'displayPrompt': message,
                   'displayPromptType': 1,
                   'options': {'imageIntention': {'needIntentionModel': True, 'backendUpdateFlag': 1}},
                   'multimedia': [], 'agentId': 'naQivTmsDa', 'version': 'v2'}
        headers = {
            'authority': 'yuanbao.tencent.com',
            'chat_version': 'v1',
            'x-agentid': 'naQivTmsDa',
            'x-id': 'null',
            'x-requested-with': 'XMLHttpRequest',
            'x-source': 'web',
            'x-token': 'null',
            'Cookie': cookie,
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'content-type': 'text/plain;charset=UTF-8'
        }
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
                async with session.post(url, headers=headers, data=json.dumps(payload), timeout=timeout) as response:
                    raw_answer = await response.text()
                    print(raw_answer)
                    if response.status == 200:
                        print(raw_answer)
                        raw_answer = await response.text()
                        end_time = asyncio.get_event_loop().time()
                        elapsed_time = end_time - start_time
                        split = re.split("data:|event:", raw_answer)
                        result = ''
                        messageId = None
                        for s in split:
                            if s.strip() != "":
                                try:
                                    loads = json.loads(s)
                                    if 'msg' in loads and 'type' in loads and loads['type'] == 'text':
                                        result += loads['msg']
                                    if 'messageId' in loads:
                                        messageId = loads['messageId']
                                except:
                                    pass
                        if messageId is not None:
                            messageId = messageId[:-2]
                        result = re.sub(r'\（.*?\）', '', result)
                        result = re.sub(r'\(.*?\)', '', result)
                        # 去掉中括号和括号里面的内容
                        result = re.sub(r'\[.*?\]', '', result)
                        result = re.sub(r'\【.*?\】', '', result)

                        await HunYuanAPIOne.delete(messageId)
                        handle_answer = result
                        # 1正常回答2超时3异常
                        status = 1
                        return result
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
                    "model": "HunYuanAPIOne",
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
    async def delete(messageId):

        url = "https://yuanbao.tencent.com/api/user/agent/conversation/v1/clear"

        payload = json.dumps({
            "conversationIds": [
                messageId
            ]
        })
        headers = {
            'authority': 'yuanbao.tencent.com',
            't-userid': 'Sb1o8mZDoJQUKdL0',
            'x-agentid': 'naQivTmsDa/fedbc20e-8b1e-4bf6-acf2-17e1cd3587a3',
            'x-commit-tag': 'bc175c12',
            'x-requested-with': 'XMLHttpRequest',
            'x-source': 'web',
            'Cookie': cookie,
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'content-type': 'application/json'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload, timeout=60) as response:
                pass

    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await HunYuanAPIOne.chat(pool=pool, prompt=prompt,
                                              question=question, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await HunYuanAPIOne.chat(pool=pool, prompt="", question="柯西与高斯的关系", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
