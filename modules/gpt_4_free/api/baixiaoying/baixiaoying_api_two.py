# 百小应https://ying.baichuan-ai.com/
import asyncio
import datetime
import os
import re
import traceback

import aiohttp
import execjs
import json

from db.mysql.mysql_jdbc import insert, create_pool, close_pool

url = "https://ying.baichuan-ai.com/api/chat/thread/runs"


class BaichuanAPITwo:
    @staticmethod
    async def chat(pool, prompt, question, timeout):
        message = f"""
                        system:
                        {prompt}
                        user:
                        {question}
                        assistant:
                        """
        payload = json.dumps({
            "thread_info": {
                "thread_id": None,
                "stream": True,
                "llm_config": {
                    "type": "bc3",
                    "retry": 3,
                    "parameters": {
                        "repetition_penalty": -1,
                        "temperature": -1,
                        "top_k": -1,
                        "top_p": -1,
                        "max_new_tokens": -1,
                        "do_sample": -1,
                        "regenerate": 0,
                        "wse": 1
                    }
                },
                "input_type": "input",
                "name": "",
                "tracing_info": {
                    "request_id": "3661135f-f1a2-446f-bd8d-2b6ca72212c8"
                },
                "messages": [
                    {
                        "id": None,
                        "type": 0,
                        "role": "user",
                        "threadId": None,
                        "messageId": "U2964018CG5ww8R",
                        "text": message,
                        "from": 0,
                        "input_type": "input",
                        "parentId": 0,
                        "createdAt": 1723449958056,
                        "attachments": []
                    }
                ],
                "history": []
            }
        })

        x_bc_sig, x_bc_ts = await BaichuanAPITwo.get_runs_sign_and_timestamp()
        headers = {
            'traceparent': '00-3fbe12b7962140f190b96b6bdb60075b-d71c89bbd6180ec8-01',
            'tracestate': 'rum=v2&browser&bc7akk1cwt@15b8e6cf488cc61&67600cf622df4b4b9c2fa1267b9a1e80&uid_8v724wlsfb55apjc',
            'x-bc-sig': x_bc_sig,
            'x-bc-ts': x_bc_ts,
            'Cookie': '_c_WBKFRo=pfJ7w5FBm8jIIznspVIPOQTPdkI7WwBaoJeAjHDp; next-auth.csrf-token=11c8479c817097818b22542ce41c050ded31274128a1e9d28d581d65495d7f17%7Cbc88b20927e3ced53ccbd8d54c51939862ff367b3487e48af97f2b7e736232ba; next-auth.callback-url=https%3A%2F%2Fchat.baichuan-ai.com; acw_tc=ac11000117234482594822866ecfce0ac053cf6dd220d0e9c118975b19f30a; next-auth.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..uYjh3MZnWVlGsd8p.HkKaEC0win6ijvJXryJoPeLNPwVCxnOTDi1GJmBd7Lgs-xLcXNuC1MyQSIULfDNfLqzc5HKHZvC6aBGQCR0xnDIvOEmsyGKH-lGoGPirUZ8IC08MluoIGFJulVRkqB5KNw-NAuOvLYKPeToQnBLO_OguqFLvIerPVKLrli7wtR0Z_tTB8POU7aF-bzafgYggPYMyQeflJkTb57XH.2j7GByG_663I9Ws8hrucKg',
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
                        split = re.split("\n", raw_answer)
                        result = ''
                        threadId = None
                        for i in split:
                            if i.strip() != '':
                                loads = json.loads(i)
                                if 'metadata' in loads:
                                    metadata = loads['metadata']
                                    if 'value' in metadata:
                                        result += metadata['value']
                                    if 'threadId' in metadata:
                                        threadId = metadata['threadId']
                        result = re.sub(r'\（.*?\）', '', result)
                        result = re.sub(r'\(.*?\)', '', result)
                        # 去掉中括号和括号里面的内容
                        result = re.sub(r'\[.*?\]', '', result)
                        result = re.sub(r'\【.*?\】', '', result)

                        await BaichuanAPITwo.delete(threadId)

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
                    "model": "BaichuanAPITwo",
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
    async def delete(threadId):

        url = "https://ying.baichuan-ai.com/api/session/delete"

        payload = json.dumps({
            "id": threadId
        })
        x_bc_sig, x_bc_ts = await BaichuanAPITwo.get_delete_sign_and_timestamp(threadId)
        headers = {
            'traceparent': '00-3fbe12b7962140f190b96b6bdb60075b-d71c89bbd6180ec8-01',
            'tracestate': 'rum=v2&browser&bc7akk1cwt@15b8e6cf488cc61&67600cf622df4b4b9c2fa1267b9a1e80&uid_8v724wlsfb55apjc',
            'x-bc-sig': x_bc_sig,
            'x-bc-ts': x_bc_ts,
            'Cookie': '_c_WBKFRo=pfJ7w5FBm8jIIznspVIPOQTPdkI7WwBaoJeAjHDp; next-auth.csrf-token=11c8479c817097818b22542ce41c050ded31274128a1e9d28d581d65495d7f17%7Cbc88b20927e3ced53ccbd8d54c51939862ff367b3487e48af97f2b7e736232ba; next-auth.callback-url=https%3A%2F%2Fchat.baichuan-ai.com; acw_tc=ac11000117234482594822866ecfce0ac053cf6dd220d0e9c118975b19f30a; next-auth.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..uYjh3MZnWVlGsd8p.HkKaEC0win6ijvJXryJoPeLNPwVCxnOTDi1GJmBd7Lgs-xLcXNuC1MyQSIULfDNfLqzc5HKHZvC6aBGQCR0xnDIvOEmsyGKH-lGoGPirUZ8IC08MluoIGFJulVRkqB5KNw-NAuOvLYKPeToQnBLO_OguqFLvIerPVKLrli7wtR0Z_tTB8POU7aF-bzafgYggPYMyQeflJkTb57XH.2j7GByG_663I9Ws8hrucKg',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload, timeout=60) as response:
                pass

    @staticmethod
    async def get_runs_sign_and_timestamp():
        """
        获取访问签名和时间戳
        """
        # 读取crypto-js库文件和你的JavaScript代码
        # 获取脚本文件所在的目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, "crypto-js.min.js"), 'r', encoding='utf-8') as file:
            crypto_js_code = file.read()

        with open(os.path.join(script_dir, "encryption_two.js"), 'r', encoding='utf-8') as file:
            script_code = file.read()

        # 整合JavaScript代码
        js_code = crypto_js_code + "\n" + script_code
        js_code = js_code.replace("[{crypto-js_path}]", script_dir.replace("\\", "\\\\"))
        # 编译JavaScript代码
        ctx = execjs.compile(js_code)

        # 执行JavaScript代码并获取结果
        result = ctx.call("runs_sign")
        return result['x-bc-sig'], result['x-bc-ts']

    @staticmethod
    async def get_delete_sign_and_timestamp(id):
        """
        获取删除签名和时间戳
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 读取crypto-js库文件和你的JavaScript代码
        with open(os.path.join(script_dir, "crypto-js.min.js"), 'r', encoding='utf-8') as file:
            crypto_js_code = file.read()

        with open(os.path.join(script_dir, "encryption.js"), 'r', encoding='utf-8') as file:
            script_code = file.read()

        # 整合JavaScript代码
        js_code = crypto_js_code + "\n" + script_code

        # 编译JavaScript代码
        ctx = execjs.compile(js_code)

        # 执行JavaScript代码并获取结果
        result = ctx.call("delete_sign", id)
        return result['x-bc-sig'], result['x-bc-ts']

    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await BaichuanAPITwo.chat(pool=pool, prompt=prompt,
                                               question=question, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await BaichuanAPITwo.chat(pool=pool, prompt="",
                                           question="怎么评价凡人歌这部电视剧", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
