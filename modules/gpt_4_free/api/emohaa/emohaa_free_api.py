"""
# 废弃了不能用
聆心智能【特长：共情能力】
功能一：对话
"""
import os

import requests
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
ERROR_LOG = f"{script_dir}\error_log.txt"

URL = "http://124.222.40.17:8007/v1/chat/completions"
URL_CHECK = "http://124.222.40.17:8007/token/check"

token = ""


# 访问https://echo.turing-world.com/，界面禁止F12,插件也拿不到Token，所想要先打开F12,再访问网页，就可以看到token了，先打开F12，再进入网页，就可以从LocalStorage中获取refresh_token

class EmohaaAPI:
    @staticmethod
    def chat(prompt, question):

        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

        payload = json.dumps({

            "model": "concise",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": question}
            ],
            # 如果使用SSE流请设置为true，默认false
            "stream": False
        })
        info = None
        try:
            response = requests.request("POST", URL, headers=headers, data=payload)
            info = response.text
            result: dict = json.loads(info)
            choices = result['choices']
            return choices[0]['message']['content']
        except:
            print(info)
            with open(ERROR_LOG, 'a', encoding='utf-8') as f:  # 打开日志文件进行追加
                f.write(info)
                f.write('\n\n')

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


if __name__ == '__main__':
    result = EmohaaAPI.chat("你是一个文学大师，能够知晓你所擅长的文学领域，能够根据用户的问题给出相关的答案。",
                            "用四个字评价一下你的过往")
    print(result)
