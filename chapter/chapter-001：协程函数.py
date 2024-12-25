from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget)
import PySide6.QtAsyncio as QtAsyncio
import asyncio
import sys


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        widget = QWidget()
        self.setCentralWidget(widget)

        layout = QVBoxLayout(widget)

        self.text = QLabel("The answer is 42.")
        layout.addWidget(self.text, alignment=Qt.AlignmentFlag.AlignCenter)

        async_trigger = QPushButton(text="What is the question?")

        # 连接协程函数
        async_trigger.clicked.connect(
            lambda: asyncio.ensure_future(self.set_text(1, "What do you get if you multiply six by nine?")))
        layout.addWidget(async_trigger, alignment=Qt.AlignmentFlag.AlignCenter)

        # 这时候程序还在初始化，事件循环还没有跑起来，所以无法执行！！！！TODO
        asyncio.ensure_future(self.set_text(5, "Who are you?"))

    async def set_text(self, duration, text):
        await asyncio.sleep(duration)
        self.text.setText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    QtAsyncio.run(handle_sigint=True)
