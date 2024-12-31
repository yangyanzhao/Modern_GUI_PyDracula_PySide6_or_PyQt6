import json
import requests

"""
权限控制API
"""
# 是否采用模拟数据
is_mock = True


def api_login_user(username, password, device, satoken=None):
    if is_mock:
        mock_data = {
            'code': 0,
            'data': {
                'token_info': {
                    'tokenName': 'satoken', 'tokenValue': 'a275b6c4-71a0-4ca8-9c83-1eebff4fb31f',
                    'isLogin': True, 'loginId': '15', 'loginType': 'login', 'tokenTimeout': -1,
                    'sessionTimeout': -1, 'tokenSessionTimeout': -2, 'tokenActiveTimeout': -1,
                    'loginDevice': 'DESKTOP-Q5H6IJT', 'tag': None
                },
                'user': {
                    'createTime': 1731847572000, 'updateTime': 1733553698000, 'creator': '1',
                    'updater': '1', 'deleted': False, 'id': 15, 'username': 'admin',
                    'avatar': 'http://test.yudao.iocoder.cn/557f12e13d781195f6c910a9986f7bff498c8b65bb5bb8b0848f43e8561c7294.jpg',
                    'password': '***********', 'nickname': '管理员', 'mobile': '15267398131', 'status': 1,
                    'allowTokenNumber': 100, 'loginIp': '0.0.0.0', 'loginDate': 1732032000000,
                    'expirationDate': 1735660800000
                },
                'token': 'a275b6c4-71a0-4ca8-9c83-1eebff4fb31f'
            },
            'msg': ''
        }
        return mock_data
    else:
        pass
    # 登录
    url = "http://124.222.40.17:48080/admin-api/account/user/login_user"

    payload = {
        'username': username,
        'password': password,
        'device': device
    }
    headers = {
        'satoken': satoken,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, params=payload,
                                data=json.dumps(payload, ensure_ascii=False))

    res = response.content.decode(encoding='utf-8')
    data = json.loads(res)
    return data


def api_token_check(satoken):
    if is_mock:
        mock_data = {
            'code': 0,
            'data': {
                'token_info': {
                    'tokenName': 'satoken', 'tokenValue': '4b226db4-486c-472f-bd0d-cc7affadb7e4',
                    'isLogin': True, 'loginId': '15', 'loginType': 'login', 'tokenTimeout': -1,
                    'sessionTimeout': -1, 'tokenSessionTimeout': -2, 'tokenActiveTimeout': -1,
                    'loginDevice': 'DESKTOP-Q5H6IJT', 'tag': None
                },
                'online_number': 1,
                'online_token_list': ['4b226db4-486c-472f-bd0d-cc7affadb7e4'],
                'user': {
                    'createTime': 1731847572000, 'updateTime': 1733553698000, 'creator': '1',
                    'updater': '1',
                    'deleted': False, 'id': 15, 'username': 'admin',
                    'avatar': 'http://test.yudao.iocoder.cn/557f12e13d781195f6c910a9986f7bff498c8b65bb5bb8b0848f43e8561c7294.jpg',
                    'password': 'admin', 'nickname': '管理员', 'mobile': '15267398131', 'status': 1,
                    'allowTokenNumber': 100, 'loginIp': '0.0.0.0', 'loginDate': 1732032000000,
                    'expirationDate': 1735660800000
                },
                'token': '4b226db4-486c-472f-bd0d-cc7affadb7e4'},
            'msg': ''
        }
        return mock_data
    else:
        # 令牌校验
        url = "http://124.222.40.17:48080/admin-api/account/user/token_check"

        payload = {
            'satoken': satoken,
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, params=payload)
        res = response.content.decode(encoding='utf-8')
        # print(f"Token校验:{payload}")
        # print(res)
        data = json.loads(res)
        # 如果Token已过期，则强行登出。
        return data


def api_logout_user_by_satoken(satoken, logout_token):
    """
    根据token登出
    :param satoken: 操作者的token
    :param logout_token: 需要登出的token
    :return:
    """
    if is_mock:
        mock_data = {'code': 0, 'data': True, 'msg': ''}
        return mock_data
    else:

        # 根据Token登出
        url = "http://124.222.40.17:48080/admin-api/account/user/logout_user_by_satoken"

        payload = {
            'satoken': satoken,
            'logout_token': logout_token,
        }
        headers = {
            'satoken': satoken,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, params=payload)
        res = response.content.decode(encoding='utf-8')
        print(f"Token登出:{payload}")
        print(res)
        data = json.loads(res)
        return data


def api_logout_user(satoken):
    if is_mock:
        mock_data = {'code': 0, 'data': True, 'msg': ''}
        return mock_data
    else:
        # 自身登出
        url = "http://124.222.40.17:48080/admin-api/account/user/logout_user"

        payload = {
            "satoken": satoken,
        }
        headers = {
            "satoken": satoken,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        res = response.content.decode(encoding='utf-8')
        print(res)
        data = json.loads(res)
        return data


def api_login_list(satoken):
    if is_mock:
        mock_data = {'code': 0, 'data': {'0c3019af-bb80-4fc9-b2b4-aaeb489d3be9': 'DESKTOP-Q5H6IJT'}, 'msg': ''}
        if mock_data['code'] == 0:
            return mock_data['data']
    else:

        # 登录列表
        url = "http://124.222.40.17:48080/admin-api/account/user/login_list"

        payload = {
            "satoken": satoken
        }
        headers = {
            "satoken": satoken,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, params=payload)

        res = response.content.decode(encoding='utf-8')
        # print(res)
        data = json.loads(res)
        # print(f"登录列表:{payload}")
        if data['code'] == 0:
            return data['data']


if __name__ == '__main__':
    login_list = api_login_list("6809c311-1652-4e5c-9105-72771a2bde2d")
    # login_list = api_login_user("test", "test", device="电脑二")
    # login_list = api_logout_user_by_satoken("b3ff8b86-8f04-40ac-8be9-4f152329c68e","59e3b164-1fe9-44bb-a056-cb1f2dad6d73")
    # login_list = api_logout_user("b3ff8b86-8f04-40ac-8be9-4f152329c68e","59e3b164-1fe9-44bb-a056-cb1f2dad6d73")
    print(login_list)
