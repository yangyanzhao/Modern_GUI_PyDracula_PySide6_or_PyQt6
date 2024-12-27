# https://internvl.intern-ai.org.cn/chat/uGbq2UXAAA7WiyuWiV1azegIAMc4jD_9O_oFqR4x7w8=/0
import asyncio
import datetime
import json
import re

import requests
from urllib.parse import quote

from db.mysql.mysql_jdbc import create_pool, close_pool

Authorization = ''


class ShushengAPIThree:
    @staticmethod
    async def chat(pool, prompt, question, timeout):
        message = f"""
                系统:{prompt}
                用户:{question}
                assistant:"""
        session_id = await ShushengAPIThree.get_session_id()
        url = f"https://internvl.intern-ai.org.cn/puyu/chats/{session_id}/records/generate"

        payload = {}

        headers = {
            'Authorization': Authorization,
            'X-Accel-Buffering': 'no',
            'mediaprompts': '',
            'prompt': quote(message, safe=""),
            'Cookie': 'acw_tc=75e252fa-ce15-4224-a07d-93bd2c9104f6da3be6e625490e7c91c1dd59e8570d60; uaa-token=eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI1MDE1MzA3MSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTcyMzYwODAxOSwicGhvbmUiOiIxNzMwNjU2ODEyNyIsImVtYWlsIjpudWxsLCJleHAiOjE3MjQyMTI4MTl9.V6eMTvLYKGTWDs5_U27VJjOSr6L9iFLPkyRu_83uAXkAmiontpIonSkZGOdc_Pa5gxlJMowCQy4aJbs_pF2LHg; ssouid=50153071; is-login=1',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'text/event-stream'
        }
        info = None
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            res = response.content.decode("utf-8")
            info = res
            print(info)
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
            await ShushengAPIThree.delete(session_id)
            if len(arr) > 0:
                return arr[-1]
        except:
            print(info)

    @staticmethod
    async def get_session_id():

        url = "https://internvl.intern-ai.org.cn/puyu/chats"

        payload = json.dumps({
            "chat_type": 0,
            "model_id": 5
        })

        headers = {
            'Authorization': Authorization,
            'Cookie': 'acw_tc=75e252fa-ce15-4224-a07d-93bd2c9104f6da3be6e625490e7c91c1dd59e8570d60; uaa-token=eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI1MDE1MzA3MSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTcyMzYwODAxOSwicGhvbmUiOiIxNzMwNjU2ODEyNyIsImVtYWlsIjpudWxsLCJleHAiOjE3MjQyMTI4MTl9.V6eMTvLYKGTWDs5_U27VJjOSr6L9iFLPkyRu_83uAXkAmiontpIonSkZGOdc_Pa5gxlJMowCQy4aJbs_pF2LHg; ssouid=50153071; is-login=1',
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
            'Cookie': 'acw_tc=75e252fa-ce15-4224-a07d-93bd2c9104f6da3be6e625490e7c91c1dd59e8570d60; uaa-token=eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI1MDE1MzA3MSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTcyMzYwODAxOSwicGhvbmUiOiIxNzMwNjU2ODEyNyIsImVtYWlsIjpudWxsLCJleHAiOjE3MjQyMTI4MTl9.V6eMTvLYKGTWDs5_U27VJjOSr6L9iFLPkyRu_83uAXkAmiontpIonSkZGOdc_Pa5gxlJMowCQy4aJbs_pF2LHg; ssouid=50153071; is-login=1',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
        }

        response = requests.request("DELETE", url, headers=headers, data=payload)

    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await ShushengAPIThree.chat(pool=pool, prompt=prompt,
                                                 question=question, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await ShushengAPIThree.chat(pool=pool, prompt="", question="拿破仑是谁", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
