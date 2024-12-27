import asyncio
import threading
import time
from concurrent.futures import Future

from db.mysql.async_utils import is_in_async_context


# 模拟协程函数
async def async_task():
    return 1


# 包装器
def run_coroutine_threadsafe_wrapper(async_task, loop, timeout):
    """
    在另一个线程中调度协程的函数
    :param async_task: 目标协程
    :param loop: 事件循环
    :param timeout: 超时时间
    :return:
    """

    def function(loop, async_task, future, timeout):
        # 使用 run_coroutine_threadsafe 调度协程
        asyncio_future = asyncio.run_coroutine_threadsafe(async_task(), loop)
        # 等待协程完成并获取结果
        try:
            result = asyncio_future.result(timeout=timeout)  # 设置超时时间
            future.set_result(result)  # 将结果设置到 future 中
        except asyncio.TimeoutError:
            future.set_exception(TimeoutError("超时了！！！"))
        except Exception as e:
            future.set_exception(e)

    def run_event_loop():
        asyncio.set_event_loop(loop)
        loop.run_forever()

    future = Future()  # 创建一个 Future 对象

    threading.Thread(target=run_event_loop, daemon=True).start()
    # 在主线程中启动另一个线程来调度协程
    threading.Thread(target=function, args=(loop, async_task, future, timeout)).start()
    # 主线程继续执行其他工作
    time.sleep(timeout)  # 这里要等待一下，否则支线程可能还没有没有，主线程已经结束了。
    # 停止事件循环
    loop.call_soon_threadsafe(loop.stop)

    # 获取并打印结果
    try:
        result = future.result(timeout=timeout)  # 设置超时时间
        return result
    except Exception as e:
        print(f"Exception: {e}")
        raise


if __name__ == "__main_1_":
    loop = asyncio.new_event_loop()
    result = run_coroutine_threadsafe_wrapper(async_task, loop, timeout=1)
    print(result)

import asyncio
import sys

from cocos_widgets.c_avatar import CAvatar
from PySide6.QtWidgets import QApplication, QPushButton
from PySide6 import QtAsyncio, QtWidgets




class DemoWidget(QtWidgets.QWidget):
    def __init__(self):
        super(DemoWidget, self).__init__()
        layout = QtWidgets.QVBoxLayout(self)
        avatar = CAvatar(shape=CAvatar.Circle, url='https://sfile.chatglm.cn/testpath/gen-1733562562484428664_0.png')
        button = QPushButton("按钮")
        button.clicked.connect(self.m3)
        layout.addWidget(button)
        layout.addWidget(avatar)
        self.m1()
        if is_in_async_context():
            # 如果处于异步上下文，则异步执行m2
            """
            1.使用 asyncio.create_task() 用于在异步上下文中并发执行多个协程。返回一个 Task 对象，不会阻塞当前协程。
            2.使用 asyncio.ensure_future() 用于确保一个对象可以被调度执行。将协程或 Future 对象包装为 Future 对象。如果传入的是协程，会将其包装为 Task 对象。如果传入的是 Future 对象，则直接返回。
            3.使用 asyncio.run_coroutine_threadsafe() 在同步函数中安全地调度协程。用于在多线程环境中调度协程。返回一个 concurrent.futures.Future 对象，可以通过它获取协程的结果或异常。不会阻塞调用线程。返回：Future 对象
            4.使用 asyncio.get_event_loop() 和 run_until_complete() 运行协程直到它完成。不会关闭事件循环。阻塞当前线程。返回：协程的返回值

            """
            self.m2()

        else:
            # 如果不处于异步上下文，则开启事件循环来执行m2
            asyncio.run(self.m2())  # 返回：协程的返回值


    def m1(self):
        # 直接调用,初始化的时候调用，尚未开启循环。
        print(f"m1{is_in_async_context()}")  # 输出：m1 False
        print('m1')

    async def m2(self):
        # 在async内部调用，在事件循环中执行。
        print(f"m2{is_in_async_context()}")  # 输出：m2 True
        print('m2')

    def m3(self):
        # 虽然是同步函数，但是出在Pyside6的事件循环中。
        print(f"m3{is_in_async_context()}")  # 输出：m3 True
        print("m3")
        if is_in_async_context():
            # 如果处于异步上下文，则异步执行m2
            # self.m4()
            loop = asyncio.get_event_loop()
            result = run_coroutine_threadsafe_wrapper(self.m4, loop, timeout=1)
            print(result)
        else:
            # 如果不处于异步上下文，则开启事件循环来执行m2
            asyncio.run(self.m4())

    async def m4(self):
        print(f"m4{is_in_async_context()}")
        print("m4")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
