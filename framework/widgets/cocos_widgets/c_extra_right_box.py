import asyncio
import logging

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import QFrame, QApplication, QVBoxLayout, QPushButton
from qasync import QEventLoop

from resources.framework.icons import icons


class CExtraRightBox(QFrame):
    def __init__(self, parent=None):
        super(CExtraRightBox, self).__init__(parent=parent)
        font = QFont()
        font.setFamily(u"Segoe UI")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        self.setObjectName(u"extraRightBox")
        self.setMinimumSize(QSize(0, 0))
        self.setMaximumSize(QSize(0, 16777215))
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)

        self.verticalLayout_7 = QVBoxLayout(self)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.themeSettingsTopDetail = QFrame(self)
        self.themeSettingsTopDetail.setObjectName(u"themeSettingsTopDetail")
        self.themeSettingsTopDetail.setMaximumSize(QSize(16777215, 3))
        self.themeSettingsTopDetail.setFrameShape(QFrame.NoFrame)
        self.themeSettingsTopDetail.setFrameShadow(QFrame.Raised)


        self.verticalLayout_7.addWidget(self.themeSettingsTopDetail)

        self.contentSettings = QFrame(self)
        self.contentSettings.setObjectName(u"contentSettings")
        self.contentSettings.setFrameShape(QFrame.NoFrame)
        self.contentSettings.setFrameShadow(QFrame.Raised)
        self.verticalLayout_13 = QVBoxLayout(self.contentSettings)
        self.verticalLayout_13.setSpacing(0)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.topMenus = QFrame(self.contentSettings)
        self.topMenus.setObjectName(u"topMenus")
        self.topMenus.setFrameShape(QFrame.NoFrame)
        self.topMenus.setFrameShadow(QFrame.Raised)
        self.verticalLayout_14 = QVBoxLayout(self.topMenus)
        self.verticalLayout_14.setSpacing(0)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.btn_message = QPushButton(parent=self.topMenus)
        self.btn_message.setText("Message")
        self.btn_message.setObjectName(u"btn_message")
        # self.leftMenuBg.leftMenuFrame.sizePolicy.setHeightForWidth(self.btn_message.sizePolicy().hasHeightForWidth())
        # self.btn_message.setSizePolicy(self.leftMenuBg.leftMenuFrame.sizePolicy)
        self.btn_message.setMinimumSize(QSize(0, 45))
        self.btn_message.setFont(font)
        self.btn_message.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_message.setLayoutDirection(Qt.LeftToRight)

        right_slash = '\\'
        self.btn_message.setStyleSheet(
            rf"background-image: url({icons['cil-envelope-open.png'].replace(right_slash, '/')});")
        self.verticalLayout_14.addWidget(self.btn_message)

        self.btn_print = QPushButton(parent=self.topMenus)
        self.btn_print.setText("Print")
        self.btn_print.setObjectName(u"btn_print")
        # self.leftMenuBg.leftMenuFrame.sizePolicy.setHeightForWidth(self.btn_print.sizePolicy().hasHeightForWidth())
        # self.btn_print.setSizePolicy(self.leftMenuBg.leftMenuFrame.sizePolicy)
        self.btn_print.setMinimumSize(QSize(0, 45))
        self.btn_print.setFont(font)
        self.btn_print.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_print.setLayoutDirection(Qt.LeftToRight)

        right_slash = '\\'
        self.btn_print.setStyleSheet(
            rf"background-image: url({icons['cil-print.png'].replace(right_slash, '/')});")
        self.verticalLayout_14.addWidget(self.btn_print)

        self.btn_logout = QPushButton(parent=self.topMenus)
        self.btn_logout.setText("Logout")
        self.btn_logout.setObjectName(u"btn_logout")
        # self.leftMenuBg.leftMenuFrame.sizePolicy.setHeightForWidth(self.btn_logout.sizePolicy().hasHeightForWidth())
        # self.btn_logout.setSizePolicy(self.leftMenuBg.leftMenuFrame.sizePolicy)
        self.btn_logout.setMinimumSize(QSize(0, 45))
        self.btn_logout.setFont(font)
        self.btn_logout.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_logout.setLayoutDirection(Qt.LeftToRight)

        right_slash = '\\'
        self.btn_logout.setStyleSheet(
            rf"background-image: url({icons['cil-account-logout.png'].replace(right_slash, '/')});")
        self.verticalLayout_14.addWidget(self.btn_logout)

        self.verticalLayout_13.addWidget(self.topMenus, 0, Qt.AlignTop)

        self.verticalLayout_7.addWidget(self.contentSettings)


if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = CExtraRightBox()
    demo_widget.setMinimumSize(QSize(300, 0))
    # 显示窗口
    demo_widget.show()
    with loop:
        loop.run_forever()
