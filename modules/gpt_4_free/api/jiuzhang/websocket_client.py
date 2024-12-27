import asyncio
import json
import traceback

import requests
import websockets

userToken = "tal173otEoz2_WoAwQiu8pY22cWYPfwCT6pwhruipIq5NN6uV8GsVKiFoRAimt1DhPMJL3fK7shlujGFX6m2yBPfZweppPuwEVpzFCsh2AKgqZHCDkcv6cRaFmPy5i-dfx3gntHn2XBs2yzYjGtf58IEBmX1fvSnT0i3uLTgaP7kPx3a0g4"
WebSocketKey = "FmGGAo9+NAx2NiA6PWudSA=="


class WebSocketClient:
    def __init__(self):
        self.session_id = None
        self.uri = "wss://openai.100tal.com/mathgpt/learning/ask/ws?" \
                   "language=cn" \
                   "&device_id=TAL1118E46FC5315330F2435B912CD79A6CCE82" \
                   "&client_id=781102" \
                   "&ver_num=1.19.01" \
                   "&x-user-source=pc" \
                   f"&x-user-token={userToken}" \
                   "&type=0" \
                   f"&session_id={self.session_id}"
        self.headers = {
            "Pragma": "no-cache",
            "Origin": "https://playground.xes1v1.cn",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Sec-WebSocket-Key": WebSocketKey,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Upgrade": "websocket",
            "Cache-Control": "no-cache",
            "Connection": "Upgrade",
            "Sec-WebSocket-Version": "13",
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits"
        }
        self.websocket = None
        self.result = ''
        self.ask_id = None
        self.running = True

    async def connect_and_send(self, message):
        self.websocket = await websockets.connect(self.uri, extra_headers=self.headers)
        await self.websocket.send(message)
        await self._receive_messages()
        await self.websocket.close()
        return self.ask_id, self.result

    async def _receive_messages(self):
        try:
            while self.running:
                response = await self.websocket.recv()
                loads = json.loads(response)
                if 'result' in loads:
                    self.result += loads['result']
                if 'ask_id' in loads:
                    self.ask_id = loads['ask_id']

                if 'status' in loads and loads['status'] == 99999:
                    self.running = False
        except websockets.exceptions.ConnectionClosed:
            traceback.print_exc()
            error = traceback.format_exc()

    @staticmethod
    async def get_session_id():
        """
        获取session_id
        """
        url = "https://openai.100tal.com/mathgpt/learning/dialogue/create"

        payload = json.dumps({"language": "cn", "type": 0})
        headers = {
            'client_id': '781102',
            'device_id': 'TAL1118E46FC5315330F2435B912CD79A6CCE82',
            'ver_num': '1.19.01',
            'x-user-source': 'pc',
            'x-user-token': userToken,
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json;charset=UTF-8'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        res = response.content.decode('utf-8')
        loads = json.loads(res)
        try:
            return loads['data']['session_id']
        except:
            print(res)

    async def run_sync(self, message):
        msg = {
            "session_id": self.session_id,
            "language": "cn",
            "example": 0,
            "ask_id": 0,
            "parent_id": 0,
            "class_type": None,
            "output_line": 0,
            "messages": [
                {
                    "role": "user",
                    "content": message,
                    "token_class": 0,
                    "token_130b": 0
                }
            ]
        }
        ask_id, result = await self.connect_and_send(json.dumps(msg))
        return ask_id, result

    async def delete(self, id):
        url = "https://openai.100tal.com/mathgpt/learning/dialogue/remove"

        payload = json.dumps({"language": "cn", "id": id})
        headers = {
            'client_id': '781102',
            'device_id': 'TAL1118E46FC5315330F2435B912CD79A6CCE82',
            'ver_num': '1.19.01',
            'x-user-source': 'pc',
            'x-user-token': userToken,
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json;charset=UTF-8'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.content.decode('utf-8')


async def main():
    client = WebSocketClient()
    # 初始化session
    client.session_id = await WebSocketClient.get_session_id()
    ask_id, result = await client.run_sync("你知道唐朝诡事录之西行吗？")
    print(ask_id)
    print(result)
    await client.delete(ask_id)


if __name__ == "__main__":
    asyncio.run(main())
