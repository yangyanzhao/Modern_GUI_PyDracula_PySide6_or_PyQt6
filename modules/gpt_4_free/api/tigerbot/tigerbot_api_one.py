import asyncio
import datetime
import json
import re
import traceback

import aiohttp

from db.mysql.mysql_jdbc import insert, create_pool, close_pool
"""
手机号码：15267398131
"""

class TigerbotAPIOne:
    @staticmethod
    async def chat(pool, prompt, question, timeout):
        session_id = await TigerbotAPIOne.get_session_id(question[:10])

        message = f"""
                                                system:
                                                {prompt}
                                                user:
                                                {question}
                                                assistant:
                                                """

        url = "https://pai.tigerobo.com/x-pai-biz/chat-backend/chatStream"

        payload = {
            "message": {
                "id": "",
                "session": f"sessions/{session_id}",
                "content": {
                    "inlineSource": message,
                    "contentType": "text/plain"
                }
            }
        }
        headers = {
            'priority': 'u=1, i',
            'token': '6889b0690a30cce236cbd967be73cbd3e290a546ccc3aab066f78b5111aecb8c',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'content-type': 'application/json;charset=UTF-8'
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
                    if response.status == 200:
                        raw_answer = await response.text()
                        end_time = asyncio.get_event_loop().time()
                        elapsed_time = end_time - start_time
                        split = re.split('data:|event:chunk', raw_answer)
                        result = ''
                        for s in split:
                            if s.strip() != "":
                                try:
                                    loads = json.loads(s)
                                    if 'messages' in loads:
                                        if 'metadata' in loads:
                                            metadata = loads['metadata']
                                            if 'streamMetadata' in metadata:
                                                streamMetadata = metadata['streamMetadata']
                                                if 'completed' in streamMetadata:
                                                    completed = streamMetadata['completed']
                                                    if completed:
                                                        continue
                                        messages = loads['messages']
                                        for message in messages:
                                            if 'content' in message:
                                                content = message['content']
                                                if 'inlineSource' in content:
                                                    inlineSource = content['inlineSource']
                                                    if inlineSource is not None:
                                                        result += inlineSource

                                except:
                                    pass
                        await TigerbotAPIOne.delete(session_id)
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
                    "model": "TigerbotAPIOne",
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
    async def delete(session_id):

        url = f"https://pai.tigerobo.com/x-pai-biz/chat-backend/sessions/{session_id}"

        payload = "{}"
        headers = {
            'priority': 'u=1, i',
            'token': '6889b0690a30cce236cbd967be73cbd3e290a546ccc3aab066f78b5111aecb8c',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'content-type': 'application/json; charset=UTF-8'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload, timeout=60) as response:
                pass

    @staticmethod
    async def get_session_id(name):
        url = "https://pai.tigerobo.com/x-pai-biz/chat-backend/sessions"

        payload = {
            "assistant": "projects/tigerbot/assistants/tigerbot-70b-chat",
            "displayName": name,
            "description": "",
            "pluginConfig": {
                "onlineSearch": {
                    "enabled": False
                },
                "documentAnalysis": {
                    "enabled": False
                },
                "imageGeneration": {
                    "enabled": False
                }
            },
            "metadata": {
                "model": "tigerbot-70b-chat"
            }
        }
        headers = {
            'priority': 'u=1, i',
            'token': '6889b0690a30cce236cbd967be73cbd3e290a546ccc3aab066f78b5111aecb8c',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'content-type': 'application/json; charset=UTF-8'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=json.dumps(payload), timeout=60) as response:
                if response.status == 200:
                    raw_answer = await response.text()
                    return json.loads(raw_answer)['id']

    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await TigerbotAPIOne.chat(pool=pool, prompt=prompt,
                                               question=question, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await TigerbotAPIOne.chat(pool=pool, prompt="", question="黄晓明是不是渣男", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
