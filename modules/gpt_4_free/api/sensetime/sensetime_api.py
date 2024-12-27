import asyncio
import datetime
import json
import re

import execjs
import requests

from db.mysql.mysql_jdbc import create_pool, close_pool

"""
手机号码：15267398131
"""
authorization = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzM4ODU3NzMsImlhdCI6MTczMzc5OTM3MywidXNlcl9pZCI6IjcxMjI5IiwibW9iaWxlIjoiVXFvTlp3RXFTU2Q5MUx3ZllOSGswUT09IiwiZW1haWwiOiIiLCJ1c2VyX25hbWUiOiIiLCJuZWNrX25hbWUiOiIiLCJwdXJwb3NlIjoiYWNjZXNzIiwibGl2ZV9pZCI6IjU1ODMwNTQ0Nzc4Nzc1NDEiLCJlbmRwb2ludCI6IndlYiIsInN5c3RlbV90eXBlIjoid2ViIiwidG9rZW5fdHlwZSI6Im1vYmlsZSJ9.p1QHl3Mmvf8jLpcsOXxb7Siho1ec1jg2_-HlTf9cG_8"


class SensetimeAPIOne:
    @staticmethod
    async def chat(pool, prompt, question, timeout):
        message = f"""
                                system:
                                {prompt}
                                user:
                                {question}
                                assistant:
                                """

        url = "https://chat.sensetime.com/api/richmodal/v1.0.2/chat"
        sign = await SensetimeAPIOne.get_sign(message)
        payload = {
            "__data__": sign}
        headers = {
            'authorization': authorization,
            'debug': 'undefined',
            'priority': 'u=1, i',
            'system-type': 'web',
            'version-code': '',
            'x-request-id': '30e5159f-55d4-49f3-b1fe-46bda08099b3',
            'Cookie': 'UM_distinctid=190e93d52b8520-0bcaa0440d727f-26001f51-1fa400-190e93d52b9a8f; CNZZDATA1281349177=866722293-1721900029-https%253A%252F%252Fgithub.com%252F%7C1722514705',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'content-type': 'application/json;charset=UTF-8'
        }
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        message = response.content.decode('utf-8')
        try:
            split = re.split(r'data:', message)
            session_id = None
            result = ''
            for i in split:
                if i.strip() != '':
                    loads = json.loads(i)
                    if 'message' in loads:
                        m = loads['message']
                        if 'session_id' in m:
                            session_id = m['session_id']
                        if 'delta' in m:
                            result += m['delta']['text']
            result = re.sub(r'\（.*?\）', '', result)
            result = re.sub(r'\(.*?\)', '', result)
            # 去掉中括号和括号里面的内容
            result = re.sub(r'\[.*?\]', '', result)
            result = re.sub(r'\【.*?\】', '', result)

            await SensetimeAPIOne.delete(session_id)

            return result
        except:
            print(message)

    @staticmethod
    async def delete(session_id):

        url = f"https://chat.sensetime.com/api/richmodal/v1.0.2/session/{session_id}"

        payload = {}
        headers = {
            'authorization': authorization,
            'debug': 'undefined',
            'priority': 'u=1, i',
            'system-type': 'web',
            'version-code': '',
            'x-request-id': '30e5159f-55d4-49f3-b1fe-46bda08099b3',
            'Cookie': 'UM_distinctid=190e93d52b8520-0bcaa0440d727f-26001f51-1fa400-190e93d52b9a8f; CNZZDATA1281349177=866722293-1721900029-https%253A%252F%252Fgithub.com%252F%7C1722514705',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'content-type': 'application/json;charset=UTF-8'
        }

        response = requests.request("DELETE", url, headers=headers, data=payload)

        return response.content.decode('utf-8')

    @staticmethod
    async def get_sign(message):
        js_code = """
        function t(e) {
            var t = (e = btoa(encodeURIComponent(e).replace(/%([0-9A-F]{2})/g, (function (e, t) {
                    return String.fromCharCode(parseInt("0x" + t))
                }
            )))).length / 2;
            e.length % 2 !== 0 && (t = e.length / 2 + 1);
            for (var n = "", r = 0; r < t; r++)
                n += e[r] + e[t + r];
            return n
        }

        function get__data__(message) {
            const e = {
                "action": "next",
                "session_id": "",
                "send_msg": [{"msg_type": "user_query", "user_query": message}],
                "channel": "chat-web",
                "client_chan": "chatOnCom",
                "parent_id": "0",
                "file_ids": []
            }
            return t(JSON.stringify(e))
        }
        """
        # 编译JavaScript代码
        ctx = execjs.compile(js_code)

        # 执行JavaScript代码并获取参数加密结果
        result = ctx.call("get__data__", message)
        return result

    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await SensetimeAPIOne.chat(pool=pool, prompt=prompt,
                                                question=question, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await SensetimeAPIOne.chat(pool=pool, prompt="", question="什么是愚民政策", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
