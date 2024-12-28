import sys

from PySide6 import QtAsyncio, QtWidgets
from PySide6.QtWidgets import QWidget, QApplication

from widgets.cocos_widgets.c_toggle import CToggle


class DemoWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(500, 500)
        layout = QtWidgets.QVBoxLayout(self)

        self.toggle = CToggle()


        layout.addWidget(self.toggle)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWindow()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
