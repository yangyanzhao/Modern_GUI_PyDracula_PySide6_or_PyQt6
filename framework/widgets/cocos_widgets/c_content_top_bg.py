import asyncio
import logging

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QApplication, QHBoxLayout
from qasync import QEventLoop

from framework.widgets.cocos_widgets.c_left_box import CLeftBox
from framework.widgets.cocos_widgets.c_right_buttons import CRightButtons


class CContentTopBg(QFrame):
    def __init__(self, parent=None):
        super(CContentTopBg, self).__init__(parent=parent)

        self.setObjectName(u"contentTopBg")
        self.setMinimumSize(QSize(0, 50))
        self.setMaximumSize(QSize(16777215, 50))
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 10, 0)

        # 顶部左侧标题
        self.leftBox = CLeftBox(self)
        self.horizontalLayout.addWidget(self.leftBox)

        # 顶部右侧按钮（设置、最小化、最大化、关闭）
        self.rightButtons = CRightButtons(self)
        self.horizontalLayout.addWidget(self.rightButtons, 0, Qt.AlignRight)


if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = CContentTopBg()
    # 显示窗口
    demo_widget.show()
    with loop:
        loop.run_forever()
