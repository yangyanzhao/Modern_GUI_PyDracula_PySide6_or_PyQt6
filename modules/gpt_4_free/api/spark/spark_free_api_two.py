"""
手机号码：15925828527
讯飞星火【特长：办公助手】
功能一：对话
功能二：AI绘图
功能三：文档解读
功能四：图像解析
"""
import asyncio
import datetime
import json
import re
import traceback

import aiohttp
import requests

from db.mysql.mysql_jdbc import insert, create_pool, close_pool

URL = "http://124.222.40.17:8005/v1/chat/completions"
URL_CHECK = "http://124.222.40.17:8005/token/check"
URL_AI_IMAGES = "http://124.222.40.17:8005/v1/images/generations"

token = "43b8e432-bd18-4122-b203-e6550c1b529b"


# https://xinghuo.xfyun.cn/iflygpt/bot/home/get
# 访问https://xinghuo.xfyun.cn/界面从Cookie获取 ssoSessionId 值，由于星火平台禁用F12开发者工具，请安装 Cookie-Editor 浏览器插件查看你的Cookie。https://www.jianshu.com/p/0ac90b46ada8；如果退出登录或重新登录将可能导致ssoSessionId失效！

class SparkAPITwo:
    @staticmethod
    async def remove_identifiers_and_content(original_string, identifier_A, identifier_B):
        # 将标识符A和B转换为正则表达式，以匹配它们及其之间的任何内容
        pattern = f"{identifier_A}.*?{identifier_B}"

        # 使用re.sub()函数替换掉匹配的模式
        modified_string = re.sub(pattern, "", original_string, flags=re.DOTALL)

        return modified_string

    @staticmethod
    async def chat(pool, prompt, question, timeout):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

        payload = json.dumps({
            # 模型名称随意填写，如果使用智能体请填写botId，如1662

            # 可以从这里全局搜索找到你想用的智能体https://xinghuo.xfyun.cn/iflygpt/bot/home/get
            # "model": "spark", 参与搜索
            "model": "silent_search",  # 无搜索
            # 目前多轮对话基于消息合并实现，某些场景可能导致能力下降且受单轮最大Token数限制
            # 如果您想获得原生的多轮对话体验，可以传入首轮消息获得的id，来接续上下文，注意如果使用这个，首轮必须传none，否则第二轮会出现[belongerr]！
            # "conversation_id": "331680774:cht000b6cfc@dx18f7a7ef0bab81c560",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": question}
            ],
            # 建议关闭联网搜索，防止干扰解读结果
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
                        content = choices[0]['message']['content']
                        # 去掉搜索的内容
                        sub = await SparkAPITwo.remove_identifiers_and_content(content, r'```searchSource', '```')
                        handle_answer = sub
                        # 1正常回答2超时3异常
                        status = 1
                        return sub
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
                    "model": "SparkAPITwo",
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
            "model": "silent_search",
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
        图片解读（失败）
        """
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

        payload = json.dumps({

            "model": "spark",
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
                    "model": "SparkAPITwo",
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
    async def main_images(description):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await SparkAPITwo.chat_images(pool=pool, description=description, timeout=60)
            return result
        finally:
            await close_pool(pool)

    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await SparkAPITwo.chat(pool=pool, question=question, prompt=prompt, timeout=timeout)
            return result
        finally:
            await close_pool(pool)
