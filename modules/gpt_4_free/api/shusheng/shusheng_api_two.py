# https://internvl.intern-ai.org.cn/chat/uGbq2UXAAA7WiyuWiV1azegIAMc4jD_9O_oFqR4x7w8=/0
import asyncio
import datetime
import json
import re

import requests
from urllib.parse import quote

from db.mysql.mysql_jdbc import create_pool, close_pool

Authorization = ''


class ShushengAPITwo:
    @staticmethod
    async def chat(pool, prompt, question, timeout):
        try:
            message = f"""
                    系统:{prompt}
                    用户:{question}
                    assistant:"""
            session_id = await ShushengAPITwo.get_session_id()
            url = f"https://internvl.intern-ai.org.cn/puyu/chats/{session_id}/records/generate"

            payload = {}

            headers = {
                'Authorization': Authorization,
                'X-Accel-Buffering': 'no',
                'mediaprompts': '',
                'prompt': quote(message, safe=""),
                'Cookie': 'acw_tc=dcfa1cde-ca50-42cd-8453-98f2353b87c2d38c46e8a98fc203a3e0f19ee8936f1e; uaa-token=eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI1MDE1MzMxNSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTcyMzYwNjk3NywicGhvbmUiOiIxNTkyNTgyODUyNyIsImVtYWlsIjpudWxsLCJleHAiOjE3MjQyMTE3Nzd9.ZxhqJhPJQWPlZmy1Nf5pMyIZmhV_x6nueSc-Np1a2mNUt0JfJEcwBbuSAjsn1dQGIZ9rx0sXKHnWj8bFEo-kpw; ssouid=50153315; is-login=1',
                'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
                'Content-Type': 'text/event-stream'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            res = response.content.decode("utf-8")
            split = re.split("id:|data:", res)
            arr = []
            for i in split:
                try:
                    loads = json.loads(i)
                    if 'code' in loads and loads['code'] == 1:
                        if 'msg' in loads:
                            arr.append(loads['msg'])

                except:
                    pass
            await ShushengAPITwo.delete(session_id)
            if len(arr) > 0:
                return arr[-1]
        except:
            pass

    @staticmethod
    async def get_session_id():

        url = "https://internvl.intern-ai.org.cn/puyu/chats"

        payload = json.dumps({
            "chat_type": 0,
            "model_id": 5
        })

        headers = {
            'Authorization': Authorization,
            'Cookie': 'acw_tc=dcfa1cde-ca50-42cd-8453-98f2353b87c2d38c46e8a98fc203a3e0f19ee8936f1e; uaa-token=eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI1MDE1MzMxNSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTcyMzYwNjk3NywicGhvbmUiOiIxNTkyNTgyODUyNyIsImVtYWlsIjpudWxsLCJleHAiOjE3MjQyMTE3Nzd9.ZxhqJhPJQWPlZmy1Nf5pMyIZmhV_x6nueSc-Np1a2mNUt0JfJEcwBbuSAjsn1dQGIZ9rx0sXKHnWj8bFEo-kpw; ssouid=50153315; is-login=1',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        res = response.content.decode("utf-8")
        try:
            loads = json.loads(res)
            return loads['data']['id']
        except:
            print(res)

    @staticmethod
    async def delete(session_id):

        url = f"https://internvl.intern-ai.org.cn/puyu/chats/{session_id}"

        payload = {}
        headers = {
            'Authorization': Authorization,
            'Cookie': 'acw_tc=dcfa1cde-ca50-42cd-8453-98f2353b87c2d38c46e8a98fc203a3e0f19ee8936f1e; uaa-token=eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI1MDE1MzMxNSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTcyMzYwNjk3NywicGhvbmUiOiIxNTkyNTgyODUyNyIsImVtYWlsIjpudWxsLCJleHAiOjE3MjQyMTE3Nzd9.ZxhqJhPJQWPlZmy1Nf5pMyIZmhV_x6nueSc-Np1a2mNUt0JfJEcwBbuSAjsn1dQGIZ9rx0sXKHnWj8bFEo-kpw; ssouid=50153315; is-login=1',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
        }

        response = requests.request("DELETE", url, headers=headers, data=payload)

    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await ShushengAPITwo.chat(pool=pool, prompt=prompt,
                                               question=question, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await ShushengAPITwo.chat(pool=pool, prompt="", question="拿破仑是谁", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
