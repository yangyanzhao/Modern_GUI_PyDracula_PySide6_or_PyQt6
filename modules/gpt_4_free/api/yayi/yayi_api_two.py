import asyncio
import datetime
import re

import json
import traceback

import aiohttp

from db.mysql.mysql_jdbc import insert, create_pool, close_pool


class YayiAPITwo:
    @staticmethod
    async def chat(pool, prompt, question, timeout):
        message = f"""
                                system:
                                {prompt}
                                user:
                                {question}
                                assistant:
                                """
        url = "https://yayi.wenge.com/chat/api/dialogue/v3/dialogueByStream"
        session_id = await YayiAPITwo.get_session_id()

        payload = json.dumps({
            "appId": "21",
            "content": message,
            "conversationId": session_id,
            "param": "{\"web_source_list\":\"\",\"temperature\":\"0.4\",\"top_k\":10,\"get_news_num\":10,\"gen_max_tokens\":4000,\"promptId\":\"21\"}",
            "categoryId": "1696103913798162016",
            "modelVersion": "YAYI-V1-30B-8K",
            "clientId": "3axirprd9ig0",
            "pluginSwitch": True
        })
        headers = {
            'Authorization': 'CHTfaau+RW6+NpbrUHWPVX2uXczuBXaAPsp/iTmG4Mc=A&sNTI0NmI2NDZkOGY2OGUzYjkzMDEyZDhlYmJkNTRhYjM=',
            'I18n': 'zh-cn',
            'Model-Version': 'YAYI-V1-30B-8K',
            'Cookie': 'token=CHTfaau+RW6+NpbrUHWPVX2uXczuBXaAPsp/iTmG4Mc; _c_WBKFRo=d7DlHecXEuUhbHWoRKojoXby1JRTU6jNMxLbuS71; _nb_ioWEgULi=; TOKEN_KEY=CHTfaau+RW6+NpbrUHWPVX2uXczuBXaAPsp/iTmG4Mc; userName=%E6%99%AE%E9%80%9A%E7%94%A8%E6%88%B78527; userId=1823982351316148225; yayiFlag=false; cvFlag=undefined; role=0; userNumber=159****8527; firstPay=true; phoneMd5=k/0dLk8wr7VY5gVF9kKdJQ; bindInfo=0; firstLogin=false; havePwd=1',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
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
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=payload, timeout=timeout) as response:
                    if response.status == 200:
                        raw_answer = await response.text()
                        end_time = asyncio.get_event_loop().time()
                        elapsed_time = end_time - start_time
                        split = re.split("data:", raw_answer)
                        r = []
                        for s in split:
                            if s.strip() != '':
                                r.append(s)
                        if len(r) > 0:
                            loads = json.loads(r[-1])
                            handle_answer = loads['answer']
                            # 1正常回答2超时3异常
                            status = 1
                            return loads['answer']
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
                "model": "YayiAPITwo",
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
    async def get_session_id():
        url = "https://yayi.wenge.com/chat/api/conversation/add/"

        payload = json.dumps({
            "appId": "21",
            "appRoleId": "1658297003183144963",
            "modelVersion": "YAYI-V1-30B-8K"
        })
        headers = {
            'Authorization': 'CHTfaau+RW6+NpbrUHWPVX2uXczuBXaAPsp/iTmG4Mc=A&sNTI0NmI2NDZkOGY2OGUzYjkzMDEyZDhlYmJkNTRhYjM=',
            'I18n': 'zh-cn',
            'Model-Version': 'YAYI-V1-30B-8K',
            'Cookie': 'token=CHTfaau+RW6+NpbrUHWPVX2uXczuBXaAPsp/iTmG4Mc; _c_WBKFRo=d7DlHecXEuUhbHWoRKojoXby1JRTU6jNMxLbuS71; _nb_ioWEgULi=; TOKEN_KEY=CHTfaau+RW6+NpbrUHWPVX2uXczuBXaAPsp/iTmG4Mc; userName=%E6%99%AE%E9%80%9A%E7%94%A8%E6%88%B78527; userId=1823982351316148225; yayiFlag=false; cvFlag=undefined; role=0; userNumber=159****8527; firstPay=true; phoneMd5=k/0dLk8wr7VY5gVF9kKdJQ; bindInfo=0; firstLogin=false; havePwd=1',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload, timeout=60) as response:
                if response.status == 200:
                    res = await response.text()
                    loads = json.loads(res)
                    return loads['data']['id']

    #             这里可能超时，需要处理一下 TODO

    @staticmethod
    def delete():
        pass

    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await YayiAPITwo.chat(pool=pool, prompt=prompt,
                                           question=question, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await YayiAPITwo.chat(pool=pool, prompt="",
                                       question="你知道恩比德吗", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
