import asyncio


def is_in_async_context():
    """
    判断同步函数是否处于异步上下文中
    :return:
    """
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False
