import asyncio
import datetime
import re
import traceback
import uuid

import aiohttp
import json

from db.mysql.mysql_jdbc import insert, create_pool, close_pool
"""
手机号码：15267398131
"""

class ShanHaiAPIOne:
    @staticmethod
    async def chat(pool, prompt, question, timeout):
        message = f"""
                                        system:
                                        {prompt}
                                        user:
                                        {question}
                                        assistant:
                                        """
        url = "https://shanhai.unisound.com/v1/invitation/custom/chat"

        payload = json.dumps({
            "reqContent": message,
            "sid": str(uuid.uuid4()),
            "name": message,
            "pluginType": 0,
            "pluginParam": ""
        })
        headers = {
            'authorizemodel': '1',
            'passportid': '',
            'priority': 'u=1, i',
            'source': '0',
            'stream': 'true',
            'Cookie': 'userInfo=nnKe4vVzxgGA/l/A/6Tgq8Zpy/T9fWrTHI5lp+IfE0GB73W0giSJsyv5wktJkEpxTfgsv+Rr03/vj2y/DfA4hQ==;token=ua_Al3z3SqiDNNkfiOwOBLm/RuH6xbt5ewxfRNa+vgA9G4Q77pNP9oEhlgWW17X4/xAJzA9zfK+1bP0LegFa8dKbiuVC7ZKGzTtmJ7yab4EZWIkXFW1KpHv/A==;clientId=580E285A235A4FCC2D87FEA2BE18D78B;JSESSIONID=979EECF4DC5CB4A7C1074F08CCC60399',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'content-type': 'application/json'
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
                async with session.post(url, headers=headers, data=payload, timeout=timeout) as response:
                    if response.status == 200:
                        raw_answer = await response.text()
                        end_time = asyncio.get_event_loop().time()
                        elapsed_time = end_time - start_time
                        split = re.split("data:|retry:", raw_answer)
                        result = ''
                        sid = None
                        for s in split:
                            if s.strip() != "":
                                try:
                                    loads = json.loads(s)
                                    if 'choices' in loads:
                                        choices = loads['choices']
                                        for choice in choices:
                                            if 'delta' in choice:
                                                delta = choice['delta']
                                                if 'content' in delta:
                                                    content = delta['content']
                                                    if content is not None:
                                                        result += content

                                    if 'sid' in loads:
                                        sid = loads['sid']
                                except:
                                    pass

                        result = re.sub(r'\（.*?\）', '', result)
                        result = re.sub(r'\(.*?\)', '', result)
                        # 去掉中括号和括号里面的内容
                        result = re.sub(r'\[.*?\]', '', result)
                        result = re.sub(r'\【.*?\】', '', result)

                        await ShanHaiAPIOne.delete(sid)
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
                    "model": "ShanHaiAPIOne",
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
    async def delete(sid):

        url = "https://shanhai.unisound.com/v1/invitation/custom/session/update"

        payload = {'name': '你怎么看詹姆斯和KD?',
                   'sid': sid,
                   'status': 1,
                   'authModel': 1}
        headers = {
            'authorizemodel': '1',
            'priority': 'u=1, i',
            'source': '0',
            'Cookie': 'userInfo=nnKe4vVzxgGA/l/A/6Tgq8Zpy/T9fWrTHI5lp+IfE0GB73W0giSJsyv5wktJkEpxTfgsv+Rr03/vj2y/DfA4hQ==;token=ua_Al3z3SqiDNNkfiOwOBLm/RuH6xbt5ewxfRNa+vgA9G4Q77pNP9oEhlgWW17X4/xAJzA9zfK+1bP0LegFa8dKbiuVC7ZKGzTtmJ7yab4EZWIkXFW1KpHv/A==;clientId=580E285A235A4FCC2D87FEA2BE18D78B;JSESSIONID=979EECF4DC5CB4A7C1074F08CCC60399; token=ua_Al3z3SqiDNNkfiOwOBLm/RuH6xbt5ewxfRNa+vgA9G4Q77pNP9oEhlgWW17X4/xAJzA9zfK+1bP0LegFa8dKbiuVC7ZKGzTtmJ7yab4EZWIkXFW1KpHv/A; clientId=580E285A235A4FCC2D87FEA2BE18D78B; JSESSIONID=DA86197780AA886F3AFE00B152C71DA0',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'content-type': 'application/json;charset=UTF-8'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=json.dumps(payload), timeout=60) as response:
                pass

    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await ShanHaiAPIOne.chat(pool=pool, prompt=prompt,
                                              question=question, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await ShanHaiAPIOne.chat(pool=pool, prompt="", question="你怎么看文班亚马和KD", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
