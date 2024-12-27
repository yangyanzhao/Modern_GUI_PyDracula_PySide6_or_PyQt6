"""
1.协程函数必须运行在事件循环中。
2.同一个线程中，事件循环不可嵌套调用。只能有一个事件循环。
3.在同步函数中调用协程：
    3.1 同步函数不处于异步上下文中，需要开启事件循环来运行协程：asyncio.run(async_func())并返回协程结果。
    3.2 同步函数处于异步上下文中：

        3.2.1 上下文事件循环处于未运行
            【启动协程】【非阻塞】
            3.2.1.1 使用 asyncio.run_coroutine_threadsafe() 在同步函数中安全地调度协程。用于在多线程环境中调度协程。返回一个 concurrent.futures.Future 对象，可以通过它获取协程的结果或异常。不会阻塞调用线程。返回：Future 对象
            【启动协程】【阻塞】
            3.2.1.2 使用 asyncio.run_until_complete() 用于在当前运行的事件循环中等待一个协程完成，这通常用于事件循环首次创建时或在主线程中执行时，因为它会阻塞当前线程，直到协程完成，且不会关闭事件循环。。

        3.2.2 上下文事件循环处于运行中
            如果事件循环整在运行中，也就是running是True,则不能直接使用该事件循环来执行新的协程，因为事件循环已经在运行中，不能再次被启动。要么调度，要阻塞。
            【调度协程】【非阻塞】
            3.2.2.1 使用 asyncio.create_task() 用于在异步上下文中并发执行多个协程,并立即调度它。不会阻塞当前协程。但是处于同步函数中，无法使用await，只能将任务返回到上个协程中进行await获取结果。,返回：Task 对象
            3.2.2.2 使用 asyncio.ensure_future() 用于确保一个对象可以被调度执行。如果传入的是协程，会将其包装为 Task 对象。如果传入的是 Future 对象，则直接返回。
"""
import asyncio


def is_in_async_context():
    """
    工具函数：判断函数是否处于异步上下文中
    :return:
    """
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


async def async_func():
    boo = is_in_async_context()
    print(f"async_func是否处于异步上下文: {boo}")
    if boo:
        print(f"async_func异步事件是否运行中：{asyncio.get_running_loop().is_running()}")
    print("异步函数被调用！")
    # 调用同步函数,直接调用会阻塞线程，也更加容易出现事件循环嵌套调用。因为在异步函数中往往是直接await调用协程，而在同步函数往往是asyncio.run协程，从而导致嵌套事件循环。
    # sync_func()
    r = await asyncio.to_thread(sync_func)  # 创建一个新的线程来运行同步函数，这样同步线程不会处于事件循环的上下文中。
    print(r)
    return "异步函数返回值"


def sync_func():
    boo = is_in_async_context()
    print(f"sync_func是否处于异步上下文: {boo}")
    if boo:
        print(f"sync_func异步事件是否运行中：{asyncio.get_running_loop().is_running()}")
    print("同步函数被调用！")

    async def sync_func_inner():
        boo = is_in_async_context()
        print(f"sync_func_inner是否处于异步上下文: {boo}")
        if boo:
            print(f"sync_func_inner异步事件是否运行中：{asyncio.get_running_loop().is_running()}")
        print("内部异步函数被调用！")
        return "内部异步函数返回值"

    r = asyncio.run(sync_func_inner())
    print(r)
    return "同步函数返回值"


if __name__ == '__main__':
    # 初始没有事件循环，使用 asyncio.run() 创建事件循环来运行协程函数。
    r = asyncio.run(async_func())
    print(r)
