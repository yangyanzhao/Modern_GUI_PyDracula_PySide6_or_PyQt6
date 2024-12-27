import asyncio
import datetime
import http.client
import json
import re
import time
import traceback

from db.mysql.mysql_jdbc import insert, create_pool, close_pool
"""
手机号码：15267398131
"""

class YiyanAPIOne:
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
            "text": message,
            "sessionId": "",
            "sessionName": message[:10],
            "parentChatId": 0,
            "type": 10,
            "model": "EB35",
            "newAppSessionId": None,
            "file_ids": [],
            "code": 0,
            "msg": "",
            "jt": "31$eyJrIj4iNyI0Iix5IkciQEhCRkxCSk9QUVJTVFVWVFE3Ii4ieG8iQSI6QT09REdCRUFGSEtHIkMiOzgiViJPVjIyOTw3OjY6QTlDIjgiMCwiSyJDIkEiOyJTIk5KUkxUIi0ibSI/InFtUWQrZj5aMFFrS3lVaTwzNF5rODxmbztVVlRrN15PUi8wXD1bXkBVYGhHVWctN0o+bTJBUmg1RDY0dURRK1tqbGJdYSoyVmk7Z2hleHlvbjBqa2pecmdSSkpXOHdLaTZvaitfRU5TRF4wW1hVYG55XSpFQFJEYD4vbktaKjpKbkBtUVZOKVZBdzZnRFdFM0dKL1BMMD1jamhjRnlbK2l3bW1vV3IyLmZ0XEt6ODFbXy5zc2hOVU82ZDV0O1hbby92K25YV0Z2ekNJVl5baWspUTdnXTE/alZUVGp4TVxyXEp6dXFlYXdacnpJK1c1O1trO05lOWw8bW83O3plNTxPPGx1c1ksQVZ6SS9bYUkzOTI9UVxkN2JQOFo2dj1aXzx5SlV3XVpgaXZfMz5sSD5fKjk2YS06SWRYR1VkS1kqXjg5PERCLGRnNDViaDBpODU6NWMvQzQvZkN5WzZzWWpednZaeFpXYmY1Vk98WnhiaDIuKmVvYjA9NXVrd1t0OWkuNHRPbV1dUl5yaTs1XS01WzpQZE1jb1x8MjJ8Njs/Omo7bEFCRD9xcXJ3Snp2d3lPelMvLE9QUTBkNjkifQ==",
            "sign": "1721768427016_1721793611554_VuWV4tvNfaWcWwUiyIGWhCV6M6SQv+/IWba7Ttbbez+bD5Wd8eor3nSiywCaibX6vflQxF7b6CAFsEHpNxUF4ppg9yqrJ0JNbcCvpNnoaJDvx729BcAiI47669Ipdh5xOJcLNxlevpY1i/OGnrwEUXoNbwzKF71v6i6Njd6AuecO791Zxk4Ee8nivyNZcFdEdBdyYl+Va6Qf4fLDy7yoaromMVK+Ybw/MK87MfTp9LtVhSjZDK/QK4PZOvnv7nlUBRUUL+xabZN4WjwaJfgWhzon63uquhQLF4OhXXWHZxS95Y14NC7pQ5/DnJHB+itD1lMR1YvqH9GOiPViLZch5pkiTMwNthrMbBShtQLwl9m78D2uMQrPTD42Q4xRv9dVWvipKWqsPxCUXea7nrRlsbnyAZozoc2zC5ISyMt5iB5+zrUMpw//5c1yQa+ZeFkVbueJmiXDNf7Ek0pNZELuhv7JL5mxTdf4d0t83Kg2hb0=",
            "timestamp": time.time(),
            "deviceType": "pc"
        })
        headers = {
            'Acs-Token': '1721768427016_1721793611554_VuWV4tvNfaWcWwUiyIGWhCV6M6SQv+/IWba7Ttbbez+bD5Wd8eor3nSiywCaibX6vflQxF7b6CAFsEHpNxUF4ppg9yqrJ0JNbcCvpNnoaJDvx729BcAiI47669Ipdh5xOJcLNxlevpY1i/OGnrwEUXoNbwzKF71v6i6Njd6AuecO791Zxk4Ee8nivyNZcFdEdBdyYl+Va6Qf4fLDy7yoaromMVK+Ybw/MK87MfTp9LtVhSjZDK/QK4PZOvnv7nlUBRUUL+xabZN4WjwaJfgWhzon63uquhQLF4OhXXWHZxS95Y14NC7pQ5/DnJHB+itD1lMR1YvqH9GOiPViLZch5pkiTMwNthrMbBShtQLwl9m78D2uMQrPTD42Q4xRv9dVWvipKWqsPxCUXea7nrRlsbnyAZozoc2zC5ISyMt5iB5+zrUMpw//5c1yQa+ZeFkVbueJmiXDNf7Ek0pNZELuhv7JL5mxTdf4d0t83Kg2hb0=',
            'Cookie': 'PSTM=1720857247; BAIDUID=944DBEF87E2D2B21920D3F60AAD2C42F:FG; BIDUPSID=746202D285DCDCF22871E055ADDF2C69; H_WISE_SIDS_BFESS=60359_60465_60444_60491_60500; BDUSS=U5Zfng2NEhXMHdLfmR4T2tGVzFmTDRsN2p3cDJZTUlaS1ozaHRUTFI5UTFMY2RtRUFBQUFBJCQAAAAAAAAAAAEAAACy6ZejzuSy~bPCyue-~QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADWgn2Y1oJ9mQ; BDUSS_BFESS=U5Zfng2NEhXMHdLfmR4T2tGVzFmTDRsN2p3cDJZTUlaS1ozaHRUTFI5UTFMY2RtRUFBQUFBJCQAAAAAAAAAAAEAAACy6ZejzuSy~bPCyue-~QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADWgn2Y1oJ9mQ; H_PS_PSSID=60359_60465_60491_60500; Hm_lvt_01e907653ac089993ee83ed00ef9c2f3=1719451520,1721734157,1721781731,1721785454; HMACCOUNT=8213761473B5E895; H_WISE_SIDS=60359_60465_60491_60500; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; delPer=0; PSINO=1; BAIDUID_BFESS=944DBEF87E2D2B21920D3F60AAD2C42F:FG; BA_HECTOR=0l8g210g0l85252k01048h2123rp791ja0ulp1v; ZFY=CxLW:ABOgSW:AmbpQbia7OBOB:AB:BPVrSgo:BsttF:BloJAU:C; __bid_n=190df5a58028064dd3f1fe; Hm_lpvt_01e907653ac089993ee83ed00ef9c2f3=1721793504; ab_sr=1.0.1_ZGNjNjIxYmE2NTMyNzRlYzc5YjdhM2RhODdiZWY3N2QyZDA1NjIzYjQ4YmRjYjVkZmU3MWQ3OTlkMzIwNzAyMzI0NmQyOGYxZGM5ZDQzZTJlZTQzNmI5MzE1ZTM4YjM4YWY0M2Y0YTY4ODFmNTg2ODQzZjFlYjYxMjRiMzYxMWViMDc5NGY0MGRmMDU5YjExNzYzMGExZGFlNWMwZjhkZmY5M2JmNGNmYTM2ZDZjZjE1ZTgxM2E5ZWUxOTdkNjAy; RT="z',
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
        try:
            conn = http.client.HTTPSConnection("yiyan.baidu.com")
            conn.request("POST", "/eb/chat/conversation/v2", payload, headers)
            res = conn.getresponse()
            data = res.read()
            message = data.decode("utf-8")
            raw_answer = message
            split = re.split(r"event:state\ndata:|event:major\ndata:|event:message\ndata:|event:quesRecommend\ndata:",
                             message)

            i_ = [i for i in split if i.strip() != '' and 'tokens_all' in i]
            result = None
            if len(i_) > 0:
                loads = json.loads(i_[-1])
                result = loads['data']['tokens_all']
            if result is None:
                print(message)
            handle_answer = result
            # 1正常回答2超时3异常
            status = 1
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
                "model": "YiyanAPIOne",
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
            result = await YiyanAPIOne.chat(pool=pool, prompt=prompt,
                                            question=question, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


async def main():
    pool = await create_pool(db='gpt_4_free')
    try:
        result = await YiyanAPIOne.chat(pool=pool, prompt="",
                                        question="你是哪個公司開發的", timeout=60)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    asyncio.run(main())
