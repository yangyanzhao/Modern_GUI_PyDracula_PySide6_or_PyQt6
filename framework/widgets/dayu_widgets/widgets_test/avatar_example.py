import sys
from framework.widgets.dayu_widgets import MTheme, MAvatar
from PySide6.QtWidgets import QApplication
from PySide6 import QtAsyncio, QtWidgets

from framework.widgets.dayu_widgets.qt import MPixmap


class DemoWidget(QtWidgets.QWidget):
    def __init__(self):
        super(DemoWidget, self).__init__()
        layout = QtWidgets.QVBoxLayout(self)
        avatar = MAvatar()
        avatar.set_dayu_image(MPixmap('zzz.svg'))
        layout.addWidget(avatar)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
