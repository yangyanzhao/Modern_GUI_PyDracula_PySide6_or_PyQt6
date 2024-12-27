"""
深度求索【特长：GPT4平替】
功能一：对话
"""
import asyncio
import datetime
import json
import traceback

import aiohttp

from db.mysql.mysql_jdbc import insert, create_pool, close_pool

URL = "http://124.222.40.17:8008/v1/chat/completions"
URL_CHECK = "http://124.222.40.17:8008/token/check"

token = "a7c9a23e8de140a0a92748f8c3b2355b"


# 访问https://chat.deepseek.com/界面F12;登录进入，由于emohaa禁用F12开发者工具，请先安装 Manage LocalStorage 插件，再从在当前页面中打开插件并点击 Export 按钮找到userToken的值，这将作为Authorization的Bearer Token值

class DeepseekAPIThree:
    @staticmethod
    async def chat(pool, prompt, question, timeout):

        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

        payload = json.dumps({
            # model必须为deepseek_chat或deepseek_code
            "model": "deepseek_chat",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": question}
            ],
            # 如果使用SSE流请设置为true，默认false
            "stream": False
        })
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
                async with session.post(URL, headers=headers, data=payload, timeout=timeout) as response:
                    if response.status == 200:
                        raw_answer = await response.text()
                        end_time = asyncio.get_event_loop().time()
                        elapsed_time = end_time - start_time
                        result: dict = json.loads(raw_answer)
                        if 'code' in result and result['code'] == -2001:
                            # 登录异常
                            # 1正常回答2超时3异常
                            status = 3
                            return None

                        choices = result['choices']
                        handle_answer = choices[0]['message']['content']
                        # 1正常回答2超时3异常
                        status = 1
                        return choices[0]['message']['content']
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
                    "model": "DeepseekAPIThree",
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
    async def token_check():
        """
        token校验有性
        """
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

        payload = json.dumps({
            "token": token
        })
        async with aiohttp.ClientSession() as session:
            async with session.post(URL_CHECK, headers=headers, data=payload, timeout=60) as response:
                pass

    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await DeepseekAPIThree.chat(pool=pool, prompt=prompt,
                                                 question=question, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(DeepseekAPIThree.main_chat("道可道，非常道"))
