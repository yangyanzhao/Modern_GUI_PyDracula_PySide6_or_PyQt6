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

# pip install PyExecJS

url = "https://ying.baichuan-ai.com/api/chat/thread/runs"


class BaichuanAPIOne:
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
                    "assistant": {},
                    "retry": 3,
                    "parameters": {
                        "repetition_penalty": -1,
                        "temperature": -1,
                        "top_k": -1,
                        "top_p": -1,
                        "max_new_tokens": -1,
                        "do_sample": -1,
                        "regenerate": 0,
                        "wse": True
                    }
                },
                "input_type": "input",
                "name": "",
                "tracing_info": {
                    "request_id": "c8e8851a-180f-4279-adba-4d45ccda4fcd",
                    "app_info": {
                        "id": 10001,
                        "name": "baichuan_web"
                    },
                    "user_info": {
                        "id": 220956,
                        "status": 1
                    }
                },
                "messages": [
                    {
                        "id": None,
                        "type": 0,
                        "role": "user",
                        "threadId": None,
                        "messageId": "U41b017PCfkpnc",
                        "text": message,
                        "from": 0,
                        "input_type": "input",
                        "parentId": 0,
                        "createdAt": 1721882506866,
                        "attachments": []
                    }
                ],
                "history": []
            },
            "retry": 3
        })
        x_bc_sig, x_bc_ts = await BaichuanAPIOne.get_runs_sign_and_timestamp()
        headers = {
            'priority': 'u=1, i',
            'x-bc-sig': x_bc_sig,
            'x-bc-ts': x_bc_ts,
            'x-requested-with': 'XMLHttpRequest',
            'Cookie': '_c_WBKFRo=xvPTs4dV9b663SRrV28YeU1tqr869dWJ0PAzjtZb; next-auth.csrf-token=e9e5b0569760e8d323521127ee3b48af403cf6a29389ca2effbc0eeb9ada9a52%7C29ab7cd94f104d4405c1182c32b84362726d5c1b1dd963f8cc3ab0d1e319188d; next-auth.callback-url=https%3A%2F%2Fchat.baichuan-ai.com; acw_tc=ac11000117218809776412627e09d5dce17ab193a9c4919c1a0faef7c9fbda; next-auth.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..qdUo9WBbj8nzN9-Y.U-eLta0CluTWtK8g05q2nyw0rm8mHY3TqV6eCtcx4QEd8r_d5LKfWrL49rXLjZiNF_ZMaededOWvOawpps1rA5CAS_FUxgbANZLlmSIODdYv59s3YiLlfzeOx96l_fz6Z9fV5fCbsnDKUR5ZJMUkjjnabpGtk2G0Y6q47veFtsngNeSRcVOTNfKBGKAXfjMWUmRhtQ1Gx_auX6me.Fy_eUuM0tmnumLKYXFfUvQ',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'content-type': 'application/json'
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

                        await BaichuanAPIOne.delete(threadId)
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
                    "model": "BaichuanAPIOne",
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
        x_bc_sig, x_bc_ts = await BaichuanAPIOne.get_delete_sign_and_timestamp(threadId)
        headers = {
            'priority': 'u=1, i',
            'x-bc-sig': x_bc_sig,
            'x-bc-ts': x_bc_ts,
            'Cookie': '_c_WBKFRo=xvPTs4dV9b663SRrV28YeU1tqr869dWJ0PAzjtZb; next-auth.csrf-token=e9e5b0569760e8d323521127ee3b48af403cf6a29389ca2effbc0eeb9ada9a52%7C29ab7cd94f104d4405c1182c32b84362726d5c1b1dd963f8cc3ab0d1e319188d; next-auth.callback-url=https%3A%2F%2Fchat.baichuan-ai.com; acw_tc=ac11000117218827783017579e09d5c2c7047ef8f2fd3713472c427fecb835; next-auth.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..OWkueFsUbq3lqGrF.awNExD2JhN9srp4JOgLJOy2qkZ_gNHB2fuLYEvroWE3V2RQDQw3qkzU31R5gTxChdeesx-eFdSAMjNs5aHvV6e4WSbO-iDXeQEAydlkrnq11r9p-hMNdaryy55VXD7CSRHUHBd-LSv8FGdVgc0pW2u0stcogfAoF_aHGAEieNB7S9ubf6xuXQ45SJkQ969lqxs0bsqsnUG_ierrp.3HzeZ2_s_S0Dfcc3EFIakA',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'content-type': 'application/json'
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

        with open(os.path.join(script_dir, "encryption.js"), 'r', encoding='utf-8') as file:
            script_code = file.read()

        # 整合JavaScript代码
        js_code = crypto_js_code + "\n" + script_code

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
        js_code = js_code.replace("[{crypto-js_path}]", script_dir.replace("\\", "\\\\"))
        # 编译JavaScript代码
        ctx = execjs.compile(js_code)

        # 执行JavaScript代码并获取结果
        result = ctx.call("delete_sign", id)
        return result['x-bc-sig'], result['x-bc-ts']

    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await BaichuanAPIOne.chat(pool=pool, prompt=prompt,
                                               question=question, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await BaichuanAPIOne.chat(pool=pool, prompt="",
                                           question="那隽与李晓月为什么走不到最后,李晓月35以后会不会很惨", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
