import asyncio
import logging

from PySide6.QtCore import QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QFrame, QApplication, QVBoxLayout, QMainWindow
from qasync import QEventLoop

from framework.app_settings import Settings
from framework.widgets.cocos_widgets.c_left_menu_frame import CLeftMenuFrame
from framework.widgets.cocos_widgets.c_top_logo_info import CTopLogoInfo


class CLeftMenuBg(QFrame):
    def __init__(self, parent=None):

        super(CLeftMenuBg, self).__init__(parent=parent)
        self.setObjectName(u"leftMenuBg")
        self.setMinimumSize(QSize(60, 0))
        self.setMaximumSize(QSize(60, 16777215))
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet(
            rf"""
            #leftMenuBg {{
                background-color: rgb(33, 37, 43);
            }}
            """
        )
        self.verticalLayout_3 = QVBoxLayout(self)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)

        # 左侧菜单LOGO信息控件
        self.topLogoInfo = CTopLogoInfo(parent=self)
        self.verticalLayout_3.addWidget(self.topLogoInfo)

        # 左侧菜单按钮列表控件
        self.leftMenuFrame = CLeftMenuFrame(self)
        # 切换显示隐藏
        self.leftMenuFrame.toggleButton.clicked.connect(lambda: self.toggleMenu(True))

        self.verticalLayout_3.addWidget(self.leftMenuFrame)

    def toggleMenu(self, enable):
        """
        切换显示和隐藏
        :param enable:
        :return:
        """
        if enable:
            # GET WIDTH
            width = self.width()
            maxExtend = Settings.MENU_WIDTH
            standard = 60

            # SET MAX WIDTH
            if width == 60:
                widthExtended = maxExtend
            else:
                widthExtended = standard

            # ANIMATION
            self.animation = QPropertyAnimation(self, b"minimumWidth")
            self.animation.setDuration(Settings.TIME_ANIMATION)
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
            self.animation.start()


if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = CLeftMenuBg()
    # 显示窗口
    demo_widget.show()
    with loop:
        loop.run_forever()
