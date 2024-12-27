import asyncio
import time

import requests
import json

from db.mysql.mysql_jdbc import create_pool, close_pool

"""
手机号码：15267398131
"""
token = "eyJhbGciOiJIUzUxMiIsInppcCI6IkdaSVAifQ.H4sIAAAAAAAA_6tWKi5NUrJSCg5y0g0Ndg1S0lFKrShQsjI0NzYztjSyNDPXUUpMTs4vzSvxTFGyMjI1NTSuBQCoDqHQNQAAAA.IDnxzhT4wCkbAVO_Bmc3L9V2mLjIWMdDyXBHY0Jyoq0hS4uvxA6PEd6K6_c8awO9uWyTIMjToV7Cy0dVmnL0sA"


class LucaAPIOne:
    @staticmethod
    async def chat(pool, prompt, question, timeout):
        try:

            message = f"""
                                    system:
                                    {prompt}
                                    user:
                                    {question}
                                    assistant:
                                    """
            conversation_id = await LucaAPIOne.create_conversation()
            child_msg_id = await LucaAPIOne.submit_msg(conversation_id, message)

            result = await LucaAPIOne.query_msg(conversation_id, child_msg_id)
            await LucaAPIOne.delete(conversation_id)
            return result
        except:
            pass

    @staticmethod
    async def create_conversation():
        url = "https://luca.cn/api/chat/v1/createConv"

        payload = json.dumps({
            "title": "新会话"
        })
        headers = {
            'token': token,
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        res = response.content.decode("utf-8")
        try:
            loads = json.loads(res)
            return loads["data"]
        except:
            print(res)

    @staticmethod
    async def submit_msg(conversationId, message):
        url = "https://luca.cn/api/chat/v1/submitMsg"

        payload = json.dumps({
            "generateType": "NORMAL",
            "conversationId": conversationId,
            "parentMessageId": "",
            "chatMessage": [
                {
                    "role": "USER",
                    "contents": [
                        {
                            "pairs": message,
                            "imageId": "",
                            "type": "TEXT"
                        }
                    ],
                    "contentLayout": f"<p>{message}</p>",
                    "id": "",
                    "parentMsgId": ""
                }
            ]
        })
        headers = {
            'token': token,
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        res = response.content.decode("utf-8")
        try:
            loads = json.loads(res)
            return loads["data"]['childMsgId']
        except:
            print(res)

    @staticmethod
    async def query_msg(conversationId, messageId):
        url = "https://luca.cn/api/chat/v1/queryMsg"

        payload = json.dumps({
            "conversationId": conversationId,
            "messageId": messageId
        })
        headers = {
            'token': token,
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }
        for i in range(60 * 5):
            time.sleep(1)
            response = requests.request("POST", url, headers=headers, data=payload)
            res = response.content.decode("utf-8")
            try:
                loads = json.loads(res)
                if loads['data']['state'] == 'END':
                    result = loads['data']['output']
                    return result
            except:
                print(res)

    @staticmethod
    async def delete(conversationId):
        import requests
        import json

        url = "https://luca.cn/api/chat/v1/deleteConv"

        payload = json.dumps({
            "convIds": [
                conversationId
            ]
        })
        headers = {
            'token': token,
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await LucaAPIOne.chat(pool=pool, prompt="", question="你知道明朝的红丸案吗", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
