"""
海螺【特长：超自然语音】
功能一：对话
功能二：语音生成（克隆）
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

URL = "http://124.222.40.17:8006/v1/chat/completions"
URL_CHECK = "http://124.222.40.17:8006/token/check"
URL_AUDIO_SPEECH = "http://124.222.40.17:8006/v1/audio/speech"
URL_AUDIO_TRANSCRIPTIONS = "http://124.222.40.17:8006/v1/audio/transcriptions"

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjY4MDY4NTYsInVzZXIiOnsiaWQiOiIyNjg0MzU4NjY0MjIyMTA1NjEiLCJuYW1lIjoi5bCP6J665bi9NTYxIiwiYXZhdGFyIjoiaHR0cHM6Ly9jZG4ueWluZ3NoaS1haS5jb20vcHJvZC91c2VyX2F2YXRhci8xNzA2MjY3NTk4ODc1ODk5OTUzLTE3MzE5NDU3MDY2ODk2NTg5Nm92ZXJzaXplLnBuZyIsImRldmljZUlEIjoiMjc4ODk4ODg0OTUyMjQ0MjMxIiwiaXNBbm9ueW1vdXMiOmZhbHNlfX0.YlCKXw7YoKMvs0VeWSa7EVysl1YjlkCEtDzsCLPB16Q"


# 访问https://hailuoai.com/界面F12从Local storage中获取到的_token

class HailuoAPIThree:
    @staticmethod
    async def chat(pool, prompt, question, timeout):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

        payload = json.dumps({
            # model模型名称可以乱填
            "model": "hailuo",
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
                        if 'code' in result and result['code'] == -1000:
                            # 強制登录
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
                    "model": "HailuoAPIThree",
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
            # model模型名称可以乱填
            "model": "hailuo",
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
            # 如果使用SSE流请设置为true，默认false
            "stream": False
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

            "model": "hailuo",
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
            # 如果使用SSE流请设置为true，默认false
            "stream": False
        })

        try:
            response = requests.request("POST", URL, headers=headers, data=payload)
            result: dict = json.loads(response.text)
            choices = result['choices']
            return choices[0]['message']['content']
        except:
            pass

    @staticmethod
    async def chat_audio_speech(content, voice="Podcast_girl"):
        """
        克隆语音
        male-botong 思远 [兼容 tts-1 alloy]
        Podcast_girl 心悦 [兼容 tts-1 echo]
        boyan_new_hailuo 子轩 [兼容 tts-1 fable]
        female-shaonv 灵儿 [兼容 tts-1 onyx]
        YaeMiko_hailuo 语嫣 [兼容 tts-1 nova]
        xiaoyi_mix_hailuo 少泽 [兼容 tts-1 shimmer]
        xiaomo_sft 芷溪 [兼容 tts-1-hd alloy]
        cove_test2_hailuo 浩翔（英文）
        scarlett_hailuo 雅涵（英文）
        Leishen2_hailuo 模仿雷电将军 [兼容 tts-1-hd echo]
        Zhongli_hailuo 模仿钟离 [兼容 tts-1-hd fable]
        Paimeng_hailuo 模仿派蒙 [兼容 tts-1-hd onyx]
        keli_hailuo 模仿可莉 [兼容 tts-1-hd nova]
        Hutao_hailuo 模仿胡桃 [兼容 tts-1-hd shimmer]
        Xionger_hailuo 模仿熊二
        Haimian_hailuo 模仿海绵宝宝
        Robot_hunter_hailuo 模仿变形金刚
        Linzhiling_hailuo 小玲玲
        huafei_hailuo 拽妃
        lingfeng_hailuo 东北er
        male_dongbei_hailuo 老铁
        Beijing_hailuo 北京er
        JayChou_hailuo JayJay
        Daniel_hailuo 潇然
        Bingjiao_zongcai_hailuo 沉韵
        female-yaoyao-hd 瑶瑶
        murong_sft 晨曦
        shangshen_sft 沐珊
        kongchen_sft 祁辰
        shenteng2_hailuo 夏洛特
        Guodegang_hailuo 郭嘚嘚
        yueyue_hailuo 小月月
        """
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

        payload = json.dumps({
            # model模型名称可以乱填
            "model": "hailuo",
            # 语音内容，尽量不要包含指令（否则可能导致模型回答你的问题）
            "input": content,
            # 发音人ID，可以使用官方或者自己克隆的音色
            "voice": voice
        })

        response = requests.request("POST", URL_AUDIO_SPEECH, headers=headers, data=payload)

        # 存储成mp3文件
        # with open("test.mp3", "wb") as f:
        #     f.write(response.content)
        return response.content

    @staticmethod
    def chat_audio_transcriptions():
        """
        语音转录
        """

        files = [
            ('file',
             (r'D:\pythonwork\pythonauto\chat\test.mp3', open(f'D:\\pythonwork\\pythonauto\\chat\\test.mp3', 'rb'),
              'audio/mpeg'))
        ]
        headers = {
            'Authorization': token,
        }
        # 创建其他参数字典
        data = {
            'model': 'hailuo',  # 这里可以乱填
            'response_format': 'json'  # 支持json或text
        }
        response = requests.request("POST", URL_AUDIO_TRANSCRIPTIONS, headers=headers, data=data,
                                    files=files)

        print(response.text)
        return response.text

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
    async def main_chat_audio_speech(content, voice):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await HailuoAPIThree.chat_audio_speech(content=content, voice=voice)
            return result
        finally:
            await close_pool(pool)

    @staticmethod
    async def main_chat(question, prompt="", timeout=60):
        pool = await create_pool(db='gpt_4_free')
        try:
            result = await HailuoAPIThree.chat(pool=pool, question=question, prompt=prompt, timeout=timeout)
            return result
        finally:
            await close_pool(pool)


if __name__ == '__main__':
    run = asyncio.run(HailuoAPIThree.main_chat(question="你是谁？", prompt=""))
    print(run)