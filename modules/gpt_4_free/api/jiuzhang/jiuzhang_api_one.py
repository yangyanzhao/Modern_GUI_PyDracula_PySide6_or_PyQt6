import asyncio
import datetime
import json
import traceback

import aiohttp

from modules.gpt_4_free.api.jiuzhang.websocket_client import WebSocketClient
from db.mysql.mysql_jdbc import insert, create_pool, close_pool

"""
通过WSS形式，不知道系统变了啥，暂未调试完成。
"""

class JiuZhangApiOne:
    @staticmethod
    async def chat(pool, prompt, question, timeout):
        message = f"""
                        system:
                        {prompt}
                        user:
                        {question}
                        assistant:
                        """
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
            client = WebSocketClient()
            ask_id, result = client.run_sync(message)
            raw_answer = result
            end_time = asyncio.get_event_loop().time()
            elapsed_time = end_time - start_time
            await JiuZhangApiOne.delete(ask_id)
            print(result)
            return result
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
                "model": "JiuZhangApiOne",
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
    async def delete(id):
        url = "https://openai.100tal.com/mathgpt/learning/dialogue/remove"

        payload = json.dumps({"language": "cn", "id": id})
        headers = {
            'client_id': '781102',
            'device_id': 'TAL1118E46FC5315330F2435B912CD79A6CCE82',
            'ver_num': '1.19.01',
            'x-user-source': 'pc',
            'x-user-token': 'tal173BWpdiPmvPfb5VSmrLgABBhwbveINZkk89nhKZ3dOIPBWniWazhJ-LNdzZgU9911Sl_MrUKYclef9GtOXCbf6Jn-idlK28WlRznIoY6t5gFEvnAZEa-CufD5bZ4irnCotp-p6tDu5Jxy7a3Ser5KX6SwtrLiBlSuL41lSklqf6-kg4',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json;charset=UTF-8'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload, timeout=60) as response:
                pass


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await JiuZhangApiOne.chat(pool=pool, prompt="", question="什么是愚民政策", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
