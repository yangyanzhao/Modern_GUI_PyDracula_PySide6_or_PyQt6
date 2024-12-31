"""
多线程插件，用于后台执行任务，防止阻塞主线程。
"""
import time
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QTextEdit
from qasync import QEventLoop

import asyncio
from PySide6.QtCore import QRunnable, QThreadPool, Signal, QObject


class WorkerSignals(QObject):
    """定义工作线程的信号"""
    finished = Signal(object)  # 完成信号，传递结果


class Worker(QRunnable):
    def __init__(self, func, *args, **kwargs):
        super(Worker, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        # 检查当前线程是否有事件循环，如果没有则创建一个
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:  # 如果没有事件循环，则创建一个新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # 运行被装饰的函数
        result = self.func(*self.args, **self.kwargs)

        # 如果函数是异步的，确保在事件循环中运行
        if asyncio.iscoroutinefunction(self.func):
            result = loop.run_until_complete(result)

        # 发出完成信号，传递结果
        self.signals.finished.emit(result)


def run_in_background(callback=None):
    """
    将函数放入后台线程中运行的装饰器
    :param callback: 可选的回调函数，接收两个参数：self 和结果
    """

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # 创建一个工作线程
            worker = Worker(func, self, *args, **kwargs)
            # 连接工作线程的 finished 信号到回调函数
            if callback:
                worker.signals.finished.connect(lambda result: callback(self, result))
            # 使用 QThreadPool 启动工作线程
            QThreadPool.globalInstance().start(worker)

        return wrapper

    return decorator


# 使用示例：
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PySide2 多线程示例")

        # 创建一个按钮和一个文本框
        self.button = QPushButton("开始任务")
        self.text_edit = QTextEdit()

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

        # 连接按钮点击事件到槽函数
        self.button.clicked.connect(self.start_task)

    @run_in_background(callback=lambda self, result: self.update_ui(result))  # 打上注解和回调函数即可
    def start_task(self, *args, **kwargs):
        # 模拟执行时间
        time.sleep(3)
        return "任务完成！"

    def update_ui(self, message):
        # 更新 UI 显示任务完成信息
        self.text_edit.append(message)


if __name__ == "__main__":
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    wx_main_widget = MainWindow()
    # 显示窗口
    wx_main_widget.show()
    with loop:
        loop.run_forever()
