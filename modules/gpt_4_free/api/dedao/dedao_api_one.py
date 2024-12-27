# https://ai.dedao.cn/so
import asyncio
import datetime
import re
import traceback

import aiohttp
import json

from db.mysql.mysql_jdbc import insert, create_pool, close_pool

"""
手机号码：15267398131
"""
cookie = "ISID=7e8367179c478ff1c7a33546b12995c4; __snaker__id=K46VBBvFncX5T6Ys; aliyungf_tc=399c281d030be5badfb65d1646bb5679a3396a008a40704c7543783bdd9f9b9c; acw_tc=ac11000117338073315271950e1c950bce012ef4afd8d9ec41abf21fb775f4; csrfToken=9q41PcnY-Wxax4vXYwZ-k9yZ; _guard_device_id=1ienfgo66yRgsjcH7aX4jlmKqTSS177N66aSxrO; gdxidpyhxdE=y%2BXayknWrR8g%2BgdgtYIL9%5CZg7xgnkP32u1YW0a3kXOnejaMwYHjiMHGfMpBSsHC8i%2FywEod1Na%2BwCStxovpRMt1bxBTlyjwrB3Dxef4JjC7i3Zx%2BCfz%2FPLt3Oeej4mKNLQ%2FGY3rreq8iTiwiyciZvL%5C2lQ2GpOGXiro4A3PZ7CD2c23d%3A1733808243443; OAUTH_SESS=H6imU99bba6eYRojS9fBePwo89FK2QKwC9qbZ4NZmm0Jb6ZcmXrYZIBP1JC-BFgk; GAT=eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJpZ2V0Z2V0LmNvbSIsImV4cCI6MTczNjM5OTM1NiwiaWF0IjoxNzMzODA3MzU2LCJpc3MiOiJEREdXIEpXVCBNSURETEVXQVJFIiwibmJmIjoxNzMzODA3MzU2LCJzdWIiOiIyMjM2OTA3NDgiLCJkZXZpY2VfaWQiOiI3ZTgzNjcxNzljNDc4ZmYxYzdhMzM1NDZiMTI5OTVjNCIsImRldmljZV90eXBlIjoiaWdldHdlYiJ9.spKDNHkvnzH-uFKHfOEcX0g5WzA4QdGX0H6pMBoVz2j4JSunFgvCiVZQqgAInD-QgCfrYmHhkcBS01KkQWGS4Q; EGG_SESS=trIrVOSyt32-rcmvFq1OMg6j3uPIIB9LICW-_9vE8oUfsScLs5Wm4UkTk8acZ28aEg9vDUqV2aAsXRsgHVvptnkHrWYmoCz9e0uINE7AjJj-EuRWdW04-2SfXIE6wbBEQe2X7x4I8rny0g9sD8Zb9UL8_nk_wX89S5_VVAgXR5JCQXKstRAxkjTkOBgy3iZeuEKwj-z8qy4tUyjgIYoz614mZKl9dCaitLv5NZfQBK-qTcE5o1e2vOv-dKYg301u63QSsx-rWuKqgtX3raNn0qsq8V0aHxnfQV5RXfjHMRAq_-_OsEk51HzCOF5PlJhHDlhStmeiCPmlG-o0EYWm3ngJH2Hfx8COidYSl8uKQQgW5FKyunDlwxcNsE5YLCukxXNnlrIqafn6IAbJ9s9SJGV5hWiB4Q4k7vk0nItlh4NnpmyXd5PnCwUjTIIS1s67ewtQuPoQy-gTpLa4vP0kvmNnmU_M0AHmzcGTCuqyfgu68niLVyRB8epsSDfrPE9QYLQTFufoe_QjIQze-_VlzLTUTB1lqibtH6pO5k39K-PTNU2KF6CfJs0MtM_xvQgtybymAzp5-YmJkv36zybHeKj4lwNlEUha5H7Xk8MMN8ZKPqMJazjeUuMrBePsxd0cKg7F7QlaTc3YBH_fxvvNfgOubt32cE1TVG1Ub7XhYH8w76OFeAIkgdhX8GYHxzMjyiKY2laHSDdER0EeEACLBINEeesKqYYUZDkE0A-48KtBSBAgQcaf6QKxUpPR5uCjQgHgwY4S0AFw7tP_HPXtRRSIR3-qzOkgImdV52A1HtbYMTS2z9jlu1E12UBEJ5WViUuc336Xarhw-SIkUi9LaUYWppw_0QZubssTrbFUfiIhJwerFzozSxySohCp4_QrucA4X5hyxSm6PabA1zsRga6YdMkHPqAwCfAeCXsqxVkT_SSc05fGdswGalmNWIRrhY2AeQ_PNtH4JS6sCv7kgaJ2GMaguir5zw4JX64jDrq4zgC7kBwNrJD1q0AmVt_9ll4N5ZmkKWyPou-flgZsEXyCF8pb_QeX3V8sTxIREjxgN0wvJPUB3hvOBJDcwfA_uqCGFedQ2aUepfdTrcWnr7vnSKhA-6YTxu0evRubgq2J5LweBZuM2oxiQ6SATecJPk1tZ8ZKD1whBV5zbMcomxCDtzmlb1gejIHT8_jyNag="


class DeDaoAPIOne:
    @staticmethod
    async def chat(pool, prompt, question, timeout):
        message = f"""
                                system:
                                {prompt}
                                user:
                                {question}
                                assistant:
                                """
        url = "https://ai.dedao.cn/assistant/access/stream"

        payload = json.dumps({
            "action": "next",
            "question_id": "",
            "query": message,
            "raw_query": message,
            "session_id": "6_MzKBqpSoLBbAXiV73zE",
            "pid_list": [],
            "pname_list": [],
            "test": "1",
            "scene": "dedao_web",
            "encry_uid": "zkZQJYbdGOe8OKpZ9kD8rVqan40jEL"
        })
        headers = {
            'Cookie': cookie,
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
                        split = re.split(r'data:|id:', raw_answer)
                        result = ''
                        for s in split:
                            s = s.replace("\n", "")
                            try:
                                loads = json.loads(s)
                                if 'data' in loads:
                                    data = loads['data']
                                    if 'msg_type' in loads:
                                        msg_type = loads['msg_type']
                                        if msg_type == 1:
                                            if 'msg' in data:
                                                result += data['msg']
                            except:
                                pass

                        handle_answer = result
                        # 1正常回答2超时3异常
                        status = 1
                        return result.replace("\n\n", "\n")
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
                    "model": "DeDaoAPIOne",
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
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await DeDaoAPIOne.chat(pool=pool, prompt=prompt,
                                            question=question, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await DeDaoAPIOne.chat(pool=pool, prompt="", question="什么是愚民政策", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
