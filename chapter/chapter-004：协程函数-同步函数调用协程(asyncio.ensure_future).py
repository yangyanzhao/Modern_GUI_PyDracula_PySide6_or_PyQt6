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


async def async_func_outer(number):
    boo = is_in_async_context()
    print(f"async_func_outer是否处于异步上下文: {boo}")
    if boo:
        print(f"async_func_outer异步事件是否运行中：{asyncio.get_running_loop().is_running()}")
    print(f"外部异步函数被调用！{number}")
    return number ** 2


async def async_func():
    def sync_func_inner():
        boo = is_in_async_context()
        print(f"sync_func_inner是否处于异步上下文: {boo}")
        if boo:
            print(f"sync_func_inner异步事件是否运行中：{asyncio.get_running_loop().is_running()}")
        print(f"内部同步函数被调用")
        # 将协程包装为Task对象
        t = asyncio.ensure_future(
            async_func_outer(10))  # 返回的是一个Task对象，它是可以被等待的，但是处于同步函数中，无法使用await，只能将任务返回到上个协程中进行await获取结果。
        # 完成时的回调函数，无论协程成功完成还是失败，都会调用这个回调函数。
        t.add_done_callback(lambda t: print(f"Task完成001，结果是：{t.result()}"))
        return t

    # 通过在协程内部直接调用同步函数，实现被调同步函数处于异步上下文之中。
    task = sync_func_inner()
    # 完成时的回调函数，无论协程成功完成还是失败，都会调用这个回调函数。
    task.add_done_callback(lambda t: print(f"Task完成002，结果是：{t.result()}"))
    task_result = await task
    print(task_result)
    return "协程函数返回值"


def sync_func():
    print(f"sync_func是否处于异步上下文: {is_in_async_context()}")
    print("同步函数被调用！")
    r = asyncio.run(async_func())
    print(r)
    return "同步函数返回值"


if __name__ == '__main__':
    sync_func()
