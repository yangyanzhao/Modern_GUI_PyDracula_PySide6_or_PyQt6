import sys

from PySide6 import QtAsyncio
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from framework.widgets.dayu_widgets.qt import MIcon

from framework.widgets.dayu_widgets import MTheme


class DemoWidget(QWidget):
    def __init__(self, parent=None):
        super(DemoWidget, self).__init__(parent)
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        button1 = QPushButton()
        button2 = QPushButton()
        button1.setIcon(MIcon("cloud_fill.svg"))
        button2.setIcon(MIcon(path="cloud_fill.svg", color="red"))
        self.layout().addWidget(button1)
        self.layout().addWidget(button2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)