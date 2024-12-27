# https://internvl.intern-ai.org.cn/chat/uGbq2UXAAA7WiyuWiV1azegIAMc4jD_9O_oFqR4x7w8=/0
import asyncio
import datetime
import json
import os
import re

import requests
from urllib.parse import quote

from db.mysql.mysql_jdbc import create_pool, close_pool
"""
手机号码：15267398131
"""
# 登录一次维持七天。。。。服了，得设置个账号密码，自动去登录 TODO
# https://internvl.intern-ai.org.cn/ 获取Authorization,有反Debugger，先打开F12并禁用Debugger，再进入网站查看某个请求头
Authorization = 'Bearer eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI1MDE2MzU0MiIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTczMzc5OTg0OCwicGhvbmUiOiIxNTI2NzM5ODEzMSIsImVtYWlsIjoiIiwiZXhwIjoxNzM0NDA0NjQ4fQ.6tGT7MuK6mG3uR-uC76L3nUqYPXRHpabH-aiqEWvJ5myFKkdQD5eTg81PJMPtEaGwUVL1CSdQz3MPni9p6jYlw'


class ShushengAPIOne:
    @staticmethod
    async def chat(pool, prompt, question, timeout):
        try:

            message = f"""
            系统:{prompt}
            用户:{question}
            assistant:"""
            session_id = await ShushengAPIOne.get_session_id()
            url = f"https://internvl.intern-ai.org.cn/puyu/chats/{session_id}/records/generate"

            payload = {}
            headers = {
                'Authorization': Authorization,
                'X-Accel-Buffering': 'no',
                'mediaprompts': '',
                'prompt': quote(message, safe=""),
                'Cookie': 'uaa-token=eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI1MDE2MzU0MiIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTcyMzU5NjE1NywicGhvbmUiOiIxNTI2NzM5ODEzMSIsImVtYWlsIjoiIiwiZXhwIjoxNzI0MjAwOTU3fQ.huxxtZKBazJEsA3riPhHE3ZByD-q0a3Sc-nXWRmics5LBebzaEVb-H1LRIDCIR3fV4IzIiUiB0d7j81_dZ5jvw; ssouid=50163542; is-login=1; acw_tc=b4a12666-0daa-9b33-bc32-24d4cd28fbdc82eef072b441408ffeee954bd5c7c4e3',
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
            await ShushengAPIOne.delete(session_id)
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
            'Cookie': 'uaa-token=eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI1MDE2MzU0MiIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTcyMzU5NjE1NywicGhvbmUiOiIxNTI2NzM5ODEzMSIsImVtYWlsIjoiIiwiZXhwIjoxNzI0MjAwOTU3fQ.huxxtZKBazJEsA3riPhHE3ZByD-q0a3Sc-nXWRmics5LBebzaEVb-H1LRIDCIR3fV4IzIiUiB0d7j81_dZ5jvw; ssouid=50163542; is-login=1; acw_tc=5c7c101f-3a93-4a11-b14b-5e806269c22fa94feb3aa745081292096babf0a31376',
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
            'Cookie': 'uaa-token=eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI1MDE2MzU0MiIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTcyMzU5NjE1NywicGhvbmUiOiIxNTI2NzM5ODEzMSIsImVtYWlsIjoiIiwiZXhwIjoxNzI0MjAwOTU3fQ.huxxtZKBazJEsA3riPhHE3ZByD-q0a3Sc-nXWRmics5LBebzaEVb-H1LRIDCIR3fV4IzIiUiB0d7j81_dZ5jvw; ssouid=50163542; is-login=1; acw_tc=59993ed1-dcef-4dd3-a31d-97fc2ece2cfed8a3e6d5c06c8cb3d3e7ea251d5b4c18',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
        }

        response = requests.request("DELETE", url, headers=headers, data=payload)

    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await ShushengAPIOne.chat(pool=pool, prompt=prompt,
                                               question=question, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await ShushengAPIOne.chat(pool=pool, prompt="", question="德川家康与丰臣秀吉", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
