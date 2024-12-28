import sys

from PySide6 import QtAsyncio
from PySide6.QtWidgets import QApplication, QMainWindow

from framework.widgets.cocos_widgets.c_title_bar.c_title_bar import CTitleBar


class DemoWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("CCredits")
        self.resize(500, 500)

        self.c_title_bar = CTitleBar(parent=self, app_parent=self)
        self.setCentralWidget(self.c_title_bar)

    def mousePressEvent(self, event):
        super(DemoWindow, self).mousePressEvent(event)
        self.dragPos = event.globalPosition().toPoint()  # 使用 globalPosition().toPoint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWindow()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
