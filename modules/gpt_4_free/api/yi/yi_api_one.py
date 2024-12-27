import asyncio
import datetime
import re
import traceback

import aiohttp
import requests
import json

from db.mysql.mysql_jdbc import insert, create_pool, close_pool

"""
手机号码：15267398131
"""
class YiApiOne:
    @staticmethod
    async def chat(pool, prompt, question, timeout):
        channel_id = await YiApiOne.get_channel(channel_name=question[:10])

        message = f"""
                                                        system:
                                                        {prompt}
                                                        user:
                                                        {question}
                                                        assistant:
                                                        """

        url = "https://api.wanzhi.com/api/v1/chat/send"

        payload = json.dumps({
            "isGetJson": True,
            "version": "1.4.0",
            "language": "zh-CN",
            "channelId": channel_id,
            "message": message,
            "model": "LING",
            "messageIds": [],
            "improveId": None,
            "richMessageId": None,
            "isImprove": False,
            "isNewChat": True,
            "action": None,
            "isGeneratePpt": False,
            "isSlidesChat": False,
            "imageUrls": [],
            "roleEnum": None,
            "pptCoordinates": "",
            "docPromptTemplateId": None
        })
        headers = {
            'App-Name': 'wanzhi-web',
            'Authorization': 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI0MjBmNzQ2YS0xNTc1LTQ0MDAtYjAxNC1iYmIzMGJhNzY4NzkiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUzNzA3MjYxLCJpYXQiOjE3MjIxNzEyNjF9.ELiM6KwI-HNnyQ1co_PN7Kdy4flpuXs0DIPU_Zad8129mn6q9VgjuG-RizyVAFKQD5Z8LY3JT01Y1hG1x4BkBg',
            'Device-Info': '{"web_id":"ZKv3fUzivzEGIy36d70OI","baidu_id":"190f96798588736c11fbeb"}',
            'Pop-Url': 'https://www.wanzhi.com/',
            'x-wanzhi-riskControlToken': '31$eyJrIj4iNyI0Iix5IkciQEdDRERLRklNSUxNVCJJIkFqIjwiNTw4OTlAOz5CPkFCSSI+IjYzIlEiSlFNTk5VUDI3Mzk6NiIzIit5IkYiQz9AQSI/IjkiUSJMSFBKUSJLImsiPSJba2tNdnozQldiQ3FTVis/SV9obD5dUms2ZjNzTU42R3VfN3ZxWU50Y3dAXix6OmYuanFxUkVRN1RsPFNbSjo5V3UyWm9SYEBRYGY3QlNCRm9LT28sU0FRZXAwcUhSc3opLHphXlwyelNAZjUrYCxfLktCPCw/ZD9qT0RVWlBZdmc2di5iPjE8XlVDaEdrS0R2PDE4Yk5tODwvVFc2Kk5aSm5IKlRAKVJfY3ZBaGdDX2xbMHBAb09pRXI7dUhtdypzSSxAb1tDdFZQLjFbWVxsZzdnZyxAa2BtaFBWNWNrb2dxTHZXLlxkclczRWpzWFVIZTdILlAwTmBpPFc1dFJMW2dNTDprKWIrV1paaThYOF13blBcPjlod1dpQXFvZVs4LG5RQFxxN3I+cS1UQmYuMFxkOzVbQDhkc2BTdW5QNnN5bm49YDtVPXdRVi9mWHUpeE5oZS9PYTRrb2FsODo4cGg4ei9VZWQtY1AvK1s+ZmQrbV5mUjYxTjluMlt4cXpeK3BeKUxVYSxiN1NhWUwqNytueWEvUGhma0FlVkhlcGhgPTx3XXdwT2JUTXw5SmxbZTctbFEwQHRWOnQ0WzZ2VGBda0FuTVVfXXNcOUVHRzI4Nj8ybGB1WnxQMHw7aGdpPT1sQmxEPEJCQUlHSktGKUt5SSpMTixWVC8wMyJ9',
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
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, data=payload, timeout=timeout) as response:
                    if response.status == 200:
                        raw_answer = await response.text()
                        end_time = asyncio.get_event_loop().time()
                        elapsed_time = end_time - start_time
                        result = ''
                        split = re.split(r"data:", raw_answer)
                        for sp in split:
                            if sp.strip() != '':
                                loads = json.loads(sp)
                                for l in loads:
                                    if 'content' in l and 'chunkId' in l:
                                        content = l['content']
                                        if content is not None:
                                            result += content
                        await YiApiOne.delete(channel_id)
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
                    "model": "YiApiOne",
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
    async def get_channel(channel_name):
        url = "https://api.wanzhi.com/api/v1/chat/getChannel"

        payload = json.dumps({
            "model": "LING",
            "templateId": "",
            "message": channel_name,
            "language": "Chinese",
            "isUpload": False
        })
        headers = {
            'App-Name': 'wanzhi-web',
            'Authorization': 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI0MjBmNzQ2YS0xNTc1LTQ0MDAtYjAxNC1iYmIzMGJhNzY4NzkiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUzNzA3MjYxLCJpYXQiOjE3MjIxNzEyNjF9.ELiM6KwI-HNnyQ1co_PN7Kdy4flpuXs0DIPU_Zad8129mn6q9VgjuG-RizyVAFKQD5Z8LY3JT01Y1hG1x4BkBg',
            'Device-Info': '{"web_id":"ZKv3fUzivzEGIy36d70OI","baidu_id":"190f96798588736c11fbeb"}',
            'Pop-Url': 'https://www.wanzhi.com/',
            'x-wanzhi-riskControlToken': '31$eyJrIj4iNyI0Iix5IkciQEdDRERLRklNSFFNSyJJIkFqIjwiNTw4OTlAOz5CPUZCQCI+IjYzIlEiSlFNTk5VUDI3Mzk6NiIzIit5IkYiQz9AQSI/IjkiUSJMSFBKUSJLImsiPSJ5PVcwLXMyP3FSYUh6dlheandvQDhyRjtzNTZvOWhKTFJTcHR4LWQzcmNjLFJLRzVjND1iaVtGaD1gL1hvQ2cvUjVqYm1BdHBac1tDMEFCLzg3Pzk5b045ai9qeVUzMnlIa1NRYWNkKTRYMClVQlotMiptLDxcPEE7d1ZIOWh4R3BNYG5vc0xyWmRzNjZWYERtOU1nNExlXjlzWDlST015N1x5SUxcQD9zKl8tPGZZRGRuXCkuQEpjO3RGK0JWUWVLV0haPTtSYz4uM2BkNkRgPU1LMm50KnFyQWRIQlpRODVncSx3cnY8cXJYXGZIRHd2S2FncU84Z2lQUDhpbTNpPFJcei8yc3B5NlI0Xyl6LE5pKjE0ZEBSLU5rSSxsLjpXN3RtK0IveGM/PyxDdj5taUEqcj9oOlAvQ3R1UjZuZ2o8cHpfYTErY2VmXHJUN0pkaGdrZjVdVFBrVEJoXEhzcCp5dVxUWTFOYUEpSnUyakBeXlBSOy1qMWQ5YjAqOFBIUVJWLGIsRG8+eDJEbFgtYS0xcmBqbFI0MzpPcFJPXTBOUylNdipYPHFyTXwzSWQ6PW05UD1uT1Q0bHFsRjtPTCo6S05fUFpFXi1mODVMSXowQmotOUpBWnxQMHw0aThqNkBqOz48bXFxSHVKRkRLKXlHSEsrVFAvMVVlNyJ9',
            'Cookie': '__bid_n=190f96798588736c11fbeb; acw_tc=2760820617221712358204382e144800193a30e02f5d21c28430211b28ee23; JSESSIONID=1837004624E295DCF73FB927F4D00032',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload, timeout=60) as response:
                if response.status == 200:
                    res = await response.text()
                    loads = json.loads(res)
                    return loads["data"]['channelId']

    @staticmethod
    async def delete(channel_id):

        url = "https://api.wanzhi.com/api/v1/channel/delete"

        payload = json.dumps({
            "channelId": channel_id
        })
        headers = {
            'App-Name': 'wanzhi-web',
            'Authorization': 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI0MjBmNzQ2YS0xNTc1LTQ0MDAtYjAxNC1iYmIzMGJhNzY4NzkiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUzNzA3MjYxLCJpYXQiOjE3MjIxNzEyNjF9.ELiM6KwI-HNnyQ1co_PN7Kdy4flpuXs0DIPU_Zad8129mn6q9VgjuG-RizyVAFKQD5Z8LY3JT01Y1hG1x4BkBg',
            'Device-Info': '{"web_id":"ZKv3fUzivzEGIy36d70OI","baidu_id":"190f96798588736c11fbeb"}',
            'Pop-Url': 'https://www.wanzhi.com/',
            'Cookie': '__bid_n=190f96798588736c11fbeb; acw_tc=2760820617221712358204382e144800193a30e02f5d21c28430211b28ee23; JSESSIONID=3262C3F9D64B855D5EA4A1A49E9FC8A7',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload, timeout=60) as response:
                pass

    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await YiApiOne.chat(pool=pool, prompt=prompt,
                                         question=question, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await YiApiOne.chat(pool=pool, prompt="",
                                     question="你会解答情感方面的问题吗", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
