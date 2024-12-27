import asyncio
import datetime
import re
import json
import traceback

import aiohttp

from db.mysql.mysql_jdbc import insert, create_pool, close_pool


class Zhinao360ApiTwo:
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
            'Cookie': '__guid=8302176.778709937275727600.1726900048195.242; __DC_sid=8302176.2368055993793115000.1726900048195.9255; sdt=122d24be-af0e-459f-a0db-924130bfcb92; __guid=161152357.3092687046534833000.1726900049365.714; Q=u%3D360H470716392%26n%3D%26le%3D%26m%3DZGH5WGWOWGWOWGWOWGWOWGWOAGV3%26qid%3D470716392%26im%3D1_t011655040b3ed000bf%26src%3Dpcw_chat%26t%3D1; __NS_Q=u%3D360H470716392%26n%3D%26le%3D%26m%3DZGH5WGWOWGWOWGWOWGWOWGWOAGV3%26qid%3D470716392%26im%3D1_t011655040b3ed000bf%26src%3Dpcw_chat%26t%3D1; T=s%3Dc903c18ac03db20ff692ac691205f517%26t%3D1726900104%26lm%3D0-1%26lf%3D2%26sk%3Db41c731e8b600bece42cec9f1827da5e%26mt%3D1726900104%26rc%3D%26v%3D2.0%26a%3D1; __NS_T=s%3Dc903c18ac03db20ff692ac691205f517%26t%3D1726900104%26lm%3D0-1%26lf%3D2%26sk%3Db41c731e8b600bece42cec9f1827da5e%26mt%3D1726900104%26rc%3D%26v%3D2.0%26a%3D1; __DC_monitor_count=3; __DC_gid=8302176.628747355.1726900048194.1726900107803.10; tfstk=flJxOe20S40DYKq8w5GlsZvecnmkDdK4nE-QINb01ULJ5Ei4Ih_bN3_J7ZfchddzBH-wnmWi0t-VQOgn-vmH0nWwu3AtDKI5Vi-75-s67K4gKOgn-Y0ZWG_5CCfHnJEJVaSOco665TN5xawbcF_fNzsdYO61CF_WVMjQGS_bGuM5zG61f-T6VbusWaZfSRdwZ3L9exvbCR9jQObKVZsPqLERNwKXHRwsbiCARn_S-K_Dk_tN6draB1xXTFSBlrghghOJyiBtES6B2CTd4KM3kgRDVF7Wvle90tQD7iXLfxtRHZCBHUq_IetJfBfJEDMFHt_Xst-gvqxJHEx2ehq_NtBDw6pAdvzfSQxpBGpZ7YLpYL8RVeMtlg89KphmgybdjSi-25PNGgW07tpdkYI2vgQnDAFa__oP2wm-25PNGgSR-m3Y_55r4',
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
                            print(f"会话ID: {conversation_id}")
                            await Zhinao360ApiTwo.delete(conversation_id)

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
                    "model": "Zhinao360ApiTwo",
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
            'Cookie': '__guid=8302176.778709937275727600.1726900048195.242; __DC_sid=8302176.2368055993793115000.1726900048195.9255; sdt=122d24be-af0e-459f-a0db-924130bfcb92; __guid=161152357.3092687046534833000.1726900049365.714; Q=u%3D360H470716392%26n%3D%26le%3D%26m%3DZGH5WGWOWGWOWGWOWGWOWGWOAGV3%26qid%3D470716392%26im%3D1_t011655040b3ed000bf%26src%3Dpcw_chat%26t%3D1; __NS_Q=u%3D360H470716392%26n%3D%26le%3D%26m%3DZGH5WGWOWGWOWGWOWGWOWGWOAGV3%26qid%3D470716392%26im%3D1_t011655040b3ed000bf%26src%3Dpcw_chat%26t%3D1; T=s%3Dc903c18ac03db20ff692ac691205f517%26t%3D1726900104%26lm%3D0-1%26lf%3D2%26sk%3Db41c731e8b600bece42cec9f1827da5e%26mt%3D1726900104%26rc%3D%26v%3D2.0%26a%3D1; __NS_T=s%3Dc903c18ac03db20ff692ac691205f517%26t%3D1726900104%26lm%3D0-1%26lf%3D2%26sk%3Db41c731e8b600bece42cec9f1827da5e%26mt%3D1726900104%26rc%3D%26v%3D2.0%26a%3D1; __DC_monitor_count=3; __DC_gid=8302176.628747355.1726900048194.1726900107803.10; tfstk=flJxOe20S40DYKq8w5GlsZvecnmkDdK4nE-QINb01ULJ5Ei4Ih_bN3_J7ZfchddzBH-wnmWi0t-VQOgn-vmH0nWwu3AtDKI5Vi-75-s67K4gKOgn-Y0ZWG_5CCfHnJEJVaSOco665TN5xawbcF_fNzsdYO61CF_WVMjQGS_bGuM5zG61f-T6VbusWaZfSRdwZ3L9exvbCR9jQObKVZsPqLERNwKXHRwsbiCARn_S-K_Dk_tN6draB1xXTFSBlrghghOJyiBtES6B2CTd4KM3kgRDVF7Wvle90tQD7iXLfxtRHZCBHUq_IetJfBfJEDMFHt_Xst-gvqxJHEx2ehq_NtBDw6pAdvzfSQxpBGpZ7YLpYL8RVeMtlg89KphmgybdjSi-25PNGgW07tpdkYI2vgQnDAFa__oP2wm-25PNGgSR-m3Y_55r4',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload, timeout=60) as response:
                pass

    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await Zhinao360ApiTwo.chat(pool=pool, prompt=prompt,
                                               question=question, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await Zhinao360ApiTwo.chat(pool=pool, prompt="",
                                            question="你知道詹姆斯吗", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
