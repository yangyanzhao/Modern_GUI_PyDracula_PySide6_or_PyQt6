import asyncio
import threading
import time
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

# 协程函数
async def async_task():
    return 1


# 在另一个线程中调度协程的函数
def function(loop):
    # 使用 run_coroutine_threadsafe 调度协程
    future = asyncio.run_coroutine_threadsafe(async_task(), loop)
    # 等待协程完成并获取结果
    try:
        result = future.result(timeout=1)  # 设置超时时间
        print(result)
    except asyncio.TimeoutError:
        print("超时了！！！")
    except Exception as e:
        print(f"{e}")


if __name__ == "__main__":
    # 创建事件循环
    loop = asyncio.new_event_loop()
    print(f"loop是否运行中：{loop.is_running()}")
    # loop 不能处于运行中。
    assert not loop.is_running()

    def run_event_loop():
        asyncio.set_event_loop(loop)
        loop.run_forever()

    threading.Thread(target=run_event_loop, daemon=True).start()
    # 在主线程中启动另一个线程来调度协程
    threading.Thread(target=function, args=(loop,)).start()
    # 主线程继续执行其他工作
    time.sleep(1)  # 这里要等待一下，否则支线程可能还没有没有，主线程已经结束了。
    print("Main thread finished")

    # 停止事件循环
    loop.call_soon_threadsafe(loop.stop)
