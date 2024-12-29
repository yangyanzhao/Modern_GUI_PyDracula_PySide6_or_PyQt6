import sys

from PySide6 import QtAsyncio
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

from framework.widgets.cocos_widgets.c_count_up import CCountUp
from framework.widgets.dayu_widgets import MTheme

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = QWidget()
    layout = QVBoxLayout()
    widget.setLayout(layout)

    countLabel = CCountUp()
    countLabel.setAlignment(Qt.AlignCenter)
    countLabel.setMinimumSize(100, 100)
    countLabel.setDuration(6000)  # 动画时间 6 秒
    layout.addWidget(countLabel)

    button1 = QPushButton("开始")
    button1.clicked.connect(lambda: countLabel.setNum(1234))
    button2 = QPushButton("重置")
    button2.clicked.connect(lambda: countLabel.reset())
    button3 = QPushButton("暂停/继续")
    button3.clicked.connect(lambda: countLabel.resume() if countLabel.isPaused() else countLabel.pause())
    layout.addWidget(button1)
    layout.addWidget(button2)
    layout.addWidget(button3)

    # 显示窗口
    widget.show()

    QtAsyncio.run(handle_sigint=True)
