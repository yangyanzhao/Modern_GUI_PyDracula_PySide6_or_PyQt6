import asyncio
import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QApplication, QHBoxLayout, QLabel
from qasync import QEventLoop


class CBottomBar(QFrame):
    def __init__(self, parent=None):
        super(CBottomBar, self).__init__(parent=parent)
        self.setObjectName(u"bottomBar")
        self.setFixedHeight(22)
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.creditsLabel = QLabel(self)
        self.creditsLabel.setText("By: Wanderson M. Pimenta")
        self.creditsLabel.setObjectName(u"creditsLabel")
        self.creditsLabel.setFixedHeight(16)
        font5 = QFont()
        font5.setFamily(u"Segoe UI")
        font5.setBold(False)
        font5.setItalic(False)
        self.creditsLabel.setFont(font5)
        self.creditsLabel.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.creditsLabel)

        self.version = QLabel(self)
        self.version.setText("v1.0.3")
        self.version.setObjectName(u"version")
        self.version.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.version)

        self.frame_size_grip = QFrame(self)
        self.frame_size_grip.setObjectName(u"frame_size_grip")
        self.frame_size_grip.setFixedWidth(20)
        self.frame_size_grip.setFrameShape(QFrame.NoFrame)
        self.frame_size_grip.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_5.addWidget(self.frame_size_grip)

if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = CBottomBar()
    # 显示窗口
    demo_widget.show()
    with loop:
        loop.run_forever()
