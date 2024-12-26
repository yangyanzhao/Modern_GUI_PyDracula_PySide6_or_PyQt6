import asyncio
import sys

from cocos_widgets.c_avatar import CAvatar
from PySide6.QtWidgets import QApplication, QPushButton
from PySide6 import QtAsyncio, QtWidgets


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
            1.使用 asyncio.create_task() 用于在异步上下文中并发执行多个协程。不会阻塞当前协程。返回：Task 对象
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
            self.m4()
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
