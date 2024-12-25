import sys

from cocos_widgets.c_avatar import CAvatar
from PySide6.QtWidgets import QApplication
from PySide6 import QtAsyncio, QtWidgets


class DemoWidget(QtWidgets.QWidget):
    def __init__(self):
        super(DemoWidget, self).__init__()
        layout = QtWidgets.QVBoxLayout(self)
        avatar = CAvatar(shape=CAvatar.Circle, url='https://sfile.chatglm.cn/testpath/gen-1733562562484428664_0.png')
        layout.addWidget(avatar)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
