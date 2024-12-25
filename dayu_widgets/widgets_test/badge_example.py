import sys
from dayu_widgets import MTheme, MAvatar, MBadge
from PySide6.QtWidgets import QApplication
from PySide6 import QtAsyncio, QtWidgets

from dayu_widgets.qt import MPixmap


class DemoWidget(QtWidgets.QWidget):
    def __init__(self):
        super(DemoWidget, self).__init__()
        layout = QtWidgets.QVBoxLayout(self)
        avatar = MAvatar.large(MPixmap("avatar.png"))
        badge = MBadge.dot(True, widget=avatar)
        layout.addWidget(badge)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    MTheme().apply(demo_widget)
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
