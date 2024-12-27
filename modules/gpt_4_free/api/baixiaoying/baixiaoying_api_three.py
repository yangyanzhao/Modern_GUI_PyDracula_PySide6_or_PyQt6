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

script_dir = os.path.dirname(os.path.abspath(__file__))
ERROR_LOG = f"{script_dir}\\error_log.txt"


class BaichuanAPIThree:
    @staticmethod
    async def chat(pool, prompt, question, timeout):
        message = f"""
                        system:
                        {prompt}
                        user:
                        {question}
                        assistant:
                        """
        payload = json.dumps({"thread_info": {"thread_id": None, "stream": True,
                                              "llm_config": {"type": "bc3", "retry": 3,
                                                             "parameters": {"repetition_penalty": -1, "temperature": -1,
                                                                            "top_k": -1, "top_p": -1,
                                                                            "max_new_tokens": -1, "do_sample": -1,
                                                                            "regenerate": 0, "wse": 1}},
                                              "input_type": "input", "name": "",
                                              "tracing_info": {"request_id": "45ecd57d-f467-4894-804c-6025b093f0e2"},
                                              "messages": [{"id": None, "type": 0, "role": "user", "threadId": None,
                                                            "messageId": "U9c98018EDpBwHB", "text": message, "from": 0,
                                                            "input_type": "input", "parentId": 0,
                                                            "createdAt": 1723614671204, "attachments": []}],
                                              "history": []}})

        x_bc_sig, x_bc_ts = await BaichuanAPIThree.get_runs_sign_and_timestamp()
        headers = {
            'tracestate': 'rum=v2&browser&bc7akk1cwt@15b8e6cf488cc61&087f871a0f0741c89299e5db67ddf3b7&uid_kpbwgf1d4u2v4kuw',
            'traceparent': '00-b7a2c0276f964e0fa0d3738001f99752-b4f3c3e9ee8764ae-01',
            'x-bc-ts': x_bc_ts,
            'x-bc-sig': x_bc_sig,
            'Cookie': '_c_WBKFRo=1TfkFTAryfepTXH49WfBFuQvEA3eX9CJSqWdfnPf; acw_tc=ac11000117236145161688142ec174263cd144901d6b48a4d180eff62a3c09; next-auth.csrf-token=a32ae6b5faa7eef69e569f376bba6e6b664321317b5372906d7a24be63252033%%7Ce8c4b76cef377459bf9a99c99973b940d6cfe830c58c376fc6ea124967af8e35; next-auth.callback-url=https%%3A%%2F%%2Fchat.baichuan-ai.com; next-auth.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..NX_Jw1a4kTbtf6F4.LGn-NhBybxVtpNgOQQmBl7UBuR5b5kDtd_iArR8OQKklyno2Rgf6hKds4BJ9ne7Q8QKZhIqo2x8YqNKAaNbqHuBfw1dstSCruUiiGOs7o0Ydo2gEiyhMYIsbRgVEj_WnSaOKmopVyVvb6s0KHv_BZ653_DBXJTv8YOWEClbnScxQOY67xmyl3qEGxdH7Vn8SGVg72ZfLdZtEbBFJ.bexEgd3O59s3FnpgMpse1Q',
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

                        await BaichuanAPIThree.delete(threadId)
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
                    "model": "BaichuanAPIThree",
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
        x_bc_sig, x_bc_ts = await BaichuanAPIThree.get_delete_sign_and_timestamp(threadId)
        headers = {
            'tracestate': 'rum=v2&browser&bc7akk1cwt@15b8e6cf488cc61&721ca0c431ec42058641db18cb6dd0a1&uid_kpbwgf1d4u2v4kuw',
            'traceparent': '00-78e79b584255492288a13fcaca5ab5dd-5f460309b3645112-01',
            'x-bc-ts': x_bc_ts,
            'x-bc-request-id': 'cde370a7-1edd-4ae9-8494-69244684f9a9',
            'x-bc-sig': x_bc_sig,
            'Cookie': '_c_WBKFRo=1TfkFTAryfepTXH49WfBFuQvEA3eX9CJSqWdfnPf; next-auth.csrf-token=a32ae6b5faa7eef69e569f376bba6e6b664321317b5372906d7a24be63252033%%7Ce8c4b76cef377459bf9a99c99973b940d6cfe830c58c376fc6ea124967af8e35; next-auth.callback-url=https%%3A%%2F%%2Fchat.baichuan-ai.com; acw_tc=ac11000117236206721118282edd9de54f424a962c367a789e6dffb7ca639b; next-auth.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..iz5OzfoynooreHQi.1cMffAnHKDJzOPzDErE-dp8MEN6q31WX1RJv08-OyKfYPbkKNkt5DFDNNPdnD1J2m2RU9EkYgOvmx2yABg6HUZmnPZqQiTEnuJxPwvrmgy1JwW45qD-KeR8NT2ThONM1zKO-ESRHFhbUx_vP-dWBEO0pdAbyJ55eSx4vseoXPJGhODjSldSzRd-Bm9kdUIhlEfQ4__aT6b6EBZc-.I6yXvw_VH3kRcqhuw0Uyiw',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload, timeout=60) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    return None

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
            result = await BaichuanAPIThree.chat(pool=pool, prompt=prompt,
                                                 question=question, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await BaichuanAPIThree.chat(pool=pool, prompt="", question="熊廷弼与孙传庭", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
