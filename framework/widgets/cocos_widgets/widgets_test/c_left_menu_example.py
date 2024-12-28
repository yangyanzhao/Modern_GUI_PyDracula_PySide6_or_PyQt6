import sys
from PySide6 import QtAsyncio, QtWidgets
from PySide6.QtWidgets import QWidget, QApplication
from framework.widgets.cocos_widgets.c_left_menu.c_left_menu import CLeftMenu


class DemoWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(500, 500)
        layout = QtWidgets.QVBoxLayout(self)

        self.left_menu = CLeftMenu(parent=self, app_parent=self)

        layout.addWidget(self.left_menu)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWindow()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
