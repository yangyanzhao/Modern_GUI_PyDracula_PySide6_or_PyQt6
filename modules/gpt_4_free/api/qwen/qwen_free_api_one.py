"""
通义千问【特长：六边形战士】
功能一：对话
功能二：AI绘图
功能三：文档解读
功能四：图像解析
"""
import asyncio
import datetime
import json
import traceback

import aiohttp
import requests

from db.mysql.mysql_jdbc import insert, create_pool, close_pool

URL = "http://124.222.40.17:8001/v1/chat/completions"
URL_CHECK = "http://124.222.40.17:8001/token/check"
URL_AI_IMAGES = "http://124.222.40.17:8001/v1/images/generations"

# 访问https://tongyi.aliyun.com/qianwen/界面F12从Cookie中获取到的以前->login_tongyi_ticket；现在是tongyi_sso_ticket
token = "ntMAHELF6sFvJ_vUTh42FKGQDI07CSIGDPxZ*3kzE_QtxJdzys6wQhFhpesE*trU0"


class QwenAPIOne:
    @staticmethod
    async def chat(pool, prompt, question, timeout):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

        payload = json.dumps({
            # model随意填写，如果不希望输出检索过程模型名称请包含silent_search
            # 如果使用kimi+智能体，model请填写智能体ID，就是浏览器地址栏上尾部的一串英文+数字20个字符的ID
            "model": "qwen",
            # 目前多轮对话基于消息合并实现，某些场景可能导致能力下降且受单轮最大Token数限制
            # 如果您想获得原生的多轮对话体验，可以传入首轮消息获得的id，来接续上下文，注意如果使用这个，首轮必须传none，否则第二轮会空响应！
            # "conversation_id": "cnndivilnl96vah411dg",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": question}
            ],
            # 是否开启联网搜索，默认false
            "use_search": False,
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
                    "model": "QwenAPIOne",
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
    def chat_document(url, question):
        """
        文档解读
        """
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

        payload = json.dumps({
            # 模型名称随意填写，如果不希望输出检索过程模型名称请包含silent_search
            "model": "kimi",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "file",
                            "file_url": {
                                "url": url
                            }
                        },
                        {
                            "type": "text",
                            "text": question
                        }
                    ]
                }
            ],
            # 建议关闭联网搜索，防止干扰解读结果
            "use_search": False
        })

        try:
            response = requests.request("POST", URL, headers=headers, data=payload)
            result: dict = json.loads(response.text)
            choices = result['choices']
            return choices[0]['message']['content']
        except:
            pass

    @staticmethod
    def chat_picture(url, question):
        """
        图片解读
        """
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

        payload = json.dumps({

            "model": "kimi",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url
                            }
                        },
                        {
                            "type": "text",
                            "text": question
                        }
                    ]
                }
            ],

            "use_search": False
        })

        try:
            response = requests.request("POST", URL, headers=headers, data=payload)
            result: dict = json.loads(response.text)
            choices = result['choices']
            return choices[0]['message']['content']
        except:
            pass

    @staticmethod
    async def chat_images(pool, description, timeout):
        """
        ai绘图
        """
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

        payload = json.dumps({
            # 可以乱填
            "model": "wanxiang",
            "prompt": description
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
                async with session.post(URL_AI_IMAGES, headers=headers, data=payload, timeout=timeout) as response:
                    if response.status == 200:
                        raw_answer = await response.text()
                        end_time = asyncio.get_event_loop().time()
                        elapsed_time = end_time - start_time
                        result: dict = json.loads(raw_answer)
                        choices = result['data']
                        handle_answer = choices[0]['url']
                        # 1正常回答2超时3异常
                        status = 1
                        return [i['url'] for i in choices]
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
                    "model": "GlmAPIOne",
                    "prompt": "AI绘图",
                    "question": None if description is None else description[:2000],
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
    def token_check():
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

        response = requests.request("POST", URL_CHECK, headers=headers, data=payload)
        print(response.text)
        return response.text

    @staticmethod
    async def main_images(description, timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await QwenAPIOne.chat_images(pool=pool, description=description, timeout=timeout)
            return result
        finally:
            await close_pool(pool)

    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await QwenAPIOne.chat(pool=pool, question=question, prompt=prompt, timeout=timeout)
            return result
        finally:
            await close_pool(pool)
