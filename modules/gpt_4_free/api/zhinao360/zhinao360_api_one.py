import asyncio
import datetime
import re
import json
import traceback

import aiohttp

from db.mysql.mysql_jdbc import insert, create_pool, close_pool

"""
手机号码：15267398131
"""


class Zhinao360ApiOne:
    @staticmethod
    async def chat(pool, prompt, question, timeout):
        message = f"""
                        system:
                        {prompt}
                        user:
                        {question}
                        assistant:
                        """
        url = "https://chat.360.com/backend-api/api/common/chat"

        payload = json.dumps({
            "conversation_id": "",
            "role": "00000001",
            "prompt": message,
            "source_type": "prophet_web",
            "is_regenerate": False,
            "is_so": True
        })
        headers = {
            'Cookie': '__guid=8302176.4388054016390922000.1723704392534.1611; sdt=df65ab23-b49f-4cc0-9a54-b0c41e34fb46; __guid=161152357.1624641116339452700.1723704394681.8945; __DC_sid=8302176.1836158613367377700.1733798147899.1887; Q=u%3D360H3488389115%26n%3D%26le%3D%26m%3DZGHlWGWOWGWOWGWOWGWOWGWOZGZk%26qid%3D3488389115%26im%3D1_t0105d6cf9b508f72c8%26src%3Dpcw_chat%26t%3D1; __NS_Q=u%3D360H3488389115%26n%3D%26le%3D%26m%3DZGHlWGWOWGWOWGWOWGWOWGWOZGZk%26qid%3D3488389115%26im%3D1_t0105d6cf9b508f72c8%26src%3Dpcw_chat%26t%3D1; T=s%3De04a8a5ceec0f2360c1f2642ef5e6521%26t%3D1733798183%26lm%3D0-1%26lf%3D2%26sk%3De716a1cd0ed20c3c777ba369a17141f7%26mt%3D1733798183%26rc%3D%26v%3D2.0%26a%3D1; __NS_T=s%3De04a8a5ceec0f2360c1f2642ef5e6521%26t%3D1733798183%26lm%3D0-1%26lf%3D2%26sk%3De716a1cd0ed20c3c777ba369a17141f7%26mt%3D1733798183%26rc%3D%26v%3D2.0%26a%3D1; __quc_silent__=1; __DC_monitor_count=5; test_cookie_enable=null; __DC_gid=8302176.196405792.1723704392534.1733798418125.31; tfstk=f44sHIcZAdvsMMjNVICEd7EfUp0Xh-_zDIGYZSLwMV3thIw4wmLtMqEIhJeIBPzVjjeIZfO9WhnthjG0FKh9XFhXlV4UbEkNIqNYUq6PUa7zs50SkTWrKA5464hJ6jpqB2FLtgmvda7zs5euIEkOzPJFVfktHqntDWLKKjTv6qevveHnijptMFCCOjDpWxLxkwLK_jMxH-3AOWHnwjovNjssI51ULqIyViQLMvTvPQmqXpNe0FLORfmteD3vkXzI1cM81PVBf4GL8yirYIWtJ7qUBXg58h38Ooe72-jyxVNYX-mQI9xILkEUMymeMhFQlAi8WDOXo7gEM-nbxTTr1VrIVPZGipFTUAZ-SSR5QWi7A0cKvItt7uPzo0UO5LDEqjwZL8QJR2nA43YrFAqwcBiklXMPO6tDmWkcPr7GiuWiXXcsY61BBomttXMPO6tDmchn1v5COdEc.',
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

                        # 使用正则表达式匹配会话ID
                        conversation_id_pattern = re.compile(r'data: CONVERSATIONID####(.*?)\s+')
                        conversation_id_match = conversation_id_pattern.search(raw_answer)

                        if conversation_id_match:
                            conversation_id = conversation_id_match.group(1)
                            await Zhinao360ApiOne.delete(conversation_id)

                        # 使用正则表达式匹配所有 event: 200 对应的数据部分
                        pattern = re.compile(r'event: 200\s+data: (.*?)\s+', re.DOTALL)
                        matches = pattern.findall(raw_answer)

                        # 拼接所有匹配到的数据部分
                        result = ''.join(matches)
                        handle_answer = result
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
                    "model": "Zhinao360ApiOne",
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
    async def delete(conversation_id):

        url = f"https://chat.360.com/backend-api/api/ai/remove/conversation/{conversation_id}?search_action="

        payload = {}
        headers = {
            'Cookie': '__guid=8302176.4388054016390922000.1723704392534.1611; sdt=df65ab23-b49f-4cc0-9a54-b0c41e34fb46; __guid=161152357.1624641116339452700.1723704394681.8945; __DC_sid=8302176.1836158613367377700.1733798147899.1887; Q=u%3D360H3488389115%26n%3D%26le%3D%26m%3DZGHlWGWOWGWOWGWOWGWOWGWOZGZk%26qid%3D3488389115%26im%3D1_t0105d6cf9b508f72c8%26src%3Dpcw_chat%26t%3D1; __NS_Q=u%3D360H3488389115%26n%3D%26le%3D%26m%3DZGHlWGWOWGWOWGWOWGWOWGWOZGZk%26qid%3D3488389115%26im%3D1_t0105d6cf9b508f72c8%26src%3Dpcw_chat%26t%3D1; T=s%3De04a8a5ceec0f2360c1f2642ef5e6521%26t%3D1733798183%26lm%3D0-1%26lf%3D2%26sk%3De716a1cd0ed20c3c777ba369a17141f7%26mt%3D1733798183%26rc%3D%26v%3D2.0%26a%3D1; __NS_T=s%3De04a8a5ceec0f2360c1f2642ef5e6521%26t%3D1733798183%26lm%3D0-1%26lf%3D2%26sk%3De716a1cd0ed20c3c777ba369a17141f7%26mt%3D1733798183%26rc%3D%26v%3D2.0%26a%3D1; __quc_silent__=1; __DC_monitor_count=5; test_cookie_enable=null; __DC_gid=8302176.196405792.1723704392534.1733798418125.31; tfstk=f44sHIcZAdvsMMjNVICEd7EfUp0Xh-_zDIGYZSLwMV3thIw4wmLtMqEIhJeIBPzVjjeIZfO9WhnthjG0FKh9XFhXlV4UbEkNIqNYUq6PUa7zs50SkTWrKA5464hJ6jpqB2FLtgmvda7zs5euIEkOzPJFVfktHqntDWLKKjTv6qevveHnijptMFCCOjDpWxLxkwLK_jMxH-3AOWHnwjovNjssI51ULqIyViQLMvTvPQmqXpNe0FLORfmteD3vkXzI1cM81PVBf4GL8yirYIWtJ7qUBXg58h38Ooe72-jyxVNYX-mQI9xILkEUMymeMhFQlAi8WDOXo7gEM-nbxTTr1VrIVPZGipFTUAZ-SSR5QWi7A0cKvItt7uPzo0UO5LDEqjwZL8QJR2nA43YrFAqwcBiklXMPO6tDmWkcPr7GiuWiXXcsY61BBomttXMPO6tDmchn1v5COdEc.',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload, timeout=60) as response:
                pass

    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await Zhinao360ApiOne.chat(pool=pool, prompt=prompt,
                                                question=question, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await Zhinao360ApiOne.chat(pool=pool, prompt="",
                                            question="你会解答情感方面的问题吗", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
