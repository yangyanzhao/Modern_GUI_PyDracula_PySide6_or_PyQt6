import sys

from PySide6 import QtAsyncio
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout

from framework.widgets.cocos_widgets.c_drawer import CDrawer
from framework.widgets.dayu_widgets import MPushButton


class DemoWidget(QWidget):
    def __init__(self):
        super(DemoWidget, self).__init__()
        self.setWindowTitle("Demo")
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        self.drawer = CDrawer(title="芋道", parent=self)

        right_btn = MPushButton("Right")
        right_btn.clicked.connect(lambda: (self.drawer.set_dayu_position(CDrawer.RightPos), self.drawer.show()))

        layout.addWidget(right_btn)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
