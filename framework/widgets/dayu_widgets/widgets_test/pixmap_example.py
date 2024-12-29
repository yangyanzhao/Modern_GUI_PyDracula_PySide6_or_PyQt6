import sys

from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel, QHBoxLayout
from PySide6 import QtAsyncio
from framework.widgets.dayu_widgets.qt import MPixmap

from framework.widgets.dayu_widgets import MTheme, dayu_theme


class DemoWidget(QWidget):
    def __init__(self, parent=None):
        super(DemoWidget, self).__init__(parent)
        self.setWindowTitle("MPushButton控件学习")
        # 布局
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.sub_layout_1 = QHBoxLayout()
        self.main_layout.addLayout(self.sub_layout_1)
        label1 = QLabel()
        label2 = QLabel()
        label3 = QLabel()
        label1.setPixmap(MPixmap("success_line.svg"))
        label2.setPixmap(MPixmap("success_line.svg", dayu_theme.success_color))
        label3.setPixmap(MPixmap("success_line.svg", '#FFc41a'))
        self.sub_layout_1.addWidget(label1)
        self.sub_layout_1.addWidget(label2)
        self.sub_layout_1.addWidget(label3)
        self.sub_layout_1.addStretch()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)