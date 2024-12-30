import asyncio
import logging

from PySide6.QtCore import QSize, QRect, Qt
from PySide6.QtGui import QFont, QCursor
from PySide6.QtWidgets import QFrame, QLabel, QApplication, QWidget, QVBoxLayout, QPushButton, QSizePolicy, QMainWindow
from qasync import QEventLoop

from framework.widgets.dayu_widgets import MTheme
from resources.framework.icons import icons


class CLeftMenuFrame(QFrame):
    def __init__(self, parent=None):
        super(CLeftMenuFrame, self).__init__(parent=parent)

        font = QFont()
        font.setFamily(u"Segoe UI")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        # 菜单
        self.setObjectName(u"leftMenuFrame")
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)
        self.verticalMenuLayout = QVBoxLayout(self)
        self.verticalMenuLayout.setSpacing(0)
        self.verticalMenuLayout.setObjectName(u"verticalMenuLayout")
        self.verticalMenuLayout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(
            rf"""
            #leftMenuFrame{{
                border-top: 3px solid rgb(44, 49, 58);
            }}
            """
        )

        self.toggleBox = QFrame(self)
        self.toggleBox.setObjectName(u"toggleBox")
        self.toggleBox.setMaximumSize(QSize(16777215, 45))
        self.toggleBox.setFrameShape(QFrame.NoFrame)
        self.toggleBox.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.toggleBox)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        # 收起、展开按钮
        self.toggleButton = QPushButton(parent=self.toggleBox)
        self.toggleButton.setText("Hide")
        self.toggleButton.setObjectName(u"toggleButton")
        self.sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.sizePolicy.setHorizontalStretch(0)
        self.sizePolicy.setVerticalStretch(0)
        self.sizePolicy.setHeightForWidth(self.toggleButton.sizePolicy().hasHeightForWidth())
        self.toggleButton.setSizePolicy(self.sizePolicy)
        self.toggleButton.setMinimumSize(QSize(0, 45))
        self.toggleButton.setFont(font)
        self.toggleButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.toggleButton.setLayoutDirection(Qt.LeftToRight)
        right_slash = '\\'
        self.toggleButton.setStyleSheet(
            rf"""
            #toggleButton {{
                background-image: url({icons['icon_menu.png'].replace(right_slash, '/')});
                background-position: left center;
                background-repeat: no-repeat;
                border: none;
                border-left: 20px solid transparent;
                background-color: rgb(37, 41, 48);
                text-align: left;
                padding-left: 44px;
                color: rgb(113, 126, 149);
            }}
            #toggleButton:hover {{
                background-color: rgb(40, 44, 52);
            }}
            #toggleButton:pressed {{
                background-color: rgb(189, 147, 249);
            }}
            """
        )

        self.verticalLayout_4.addWidget(self.toggleButton)

        self.verticalMenuLayout.addWidget(self.toggleBox)

        # 左侧菜单
        self.topMenu = QFrame(self)
        self.topMenu.setObjectName(u"topMenu")
        self.topMenu.setFrameShape(QFrame.NoFrame)
        self.topMenu.setFrameShadow(QFrame.Raised)
        self.topMenu.setStyleSheet(
            rf"""
            #topMenu .QPushButton {{
                background-position: left center;
                background-repeat: no-repeat;
                border: none;
                border-left: 22px solid transparent;
                background-color: transparent;
                text-align: left;
                padding-left: 44px;
            }}
            #topMenu .QPushButton:hover {{
                background-color: rgb(40, 44, 52);
            }}
            #topMenu .QPushButton:pressed {{
                background-color: rgb(189, 147, 249);
                color: rgb(255, 255, 255);
            }}
            """
        )
        # 左侧菜单Layout
        self.topMenuLayout = QVBoxLayout(self.topMenu)
        self.topMenuLayout.setSpacing(0)
        self.topMenuLayout.setObjectName(u"topMenuLayout")
        self.topMenuLayout.setContentsMargins(0, 0, 0, 0)

        self.btn_home = QPushButton(parent=self.topMenu)
        self.btn_home.setText("Home")
        self.btn_home.setObjectName(u"btn_home")
        self.sizePolicy.setHeightForWidth(self.btn_home.sizePolicy().hasHeightForWidth())
        self.btn_home.setSizePolicy(self.sizePolicy)
        self.btn_home.setMinimumSize(QSize(0, 45))
        self.btn_home.setFont(font)
        self.btn_home.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_home.setLayoutDirection(Qt.LeftToRight)
        right_slash = '\\'
        self.btn_home.setStyleSheet(rf"background-image: url({icons['cil-home.png'].replace(right_slash, '/')});")

        self.topMenuLayout.addWidget(self.btn_home)

        self.btn_widgets = QPushButton(parent=self.topMenu)
        self.btn_widgets.setText("Widgets")
        self.btn_widgets.setObjectName(u"btn_widgets")
        self.sizePolicy.setHeightForWidth(self.btn_widgets.sizePolicy().hasHeightForWidth())
        self.btn_widgets.setSizePolicy(self.sizePolicy)
        self.btn_widgets.setMinimumSize(QSize(0, 45))
        self.btn_widgets.setFont(font)
        self.btn_widgets.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_widgets.setLayoutDirection(Qt.LeftToRight)

        right_slash = '\\'
        self.btn_widgets.setStyleSheet(rf"background-image: url({icons['cil-gamepad.png'].replace(right_slash, '/')});")
        self.topMenuLayout.addWidget(self.btn_widgets)

        self.btn_new = QPushButton(parent=self.topMenu)
        self.btn_new.setText("New")
        self.btn_new.setObjectName(u"btn_new")
        self.sizePolicy.setHeightForWidth(self.btn_new.sizePolicy().hasHeightForWidth())
        self.btn_new.setSizePolicy(self.sizePolicy)
        self.btn_new.setMinimumSize(QSize(0, 45))
        self.btn_new.setFont(font)
        self.btn_new.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_new.setLayoutDirection(Qt.LeftToRight)

        right_slash = '\\'
        self.btn_new.setStyleSheet(rf"background-image: url({icons['cil-file.png'].replace(right_slash, '/')});")
        self.topMenuLayout.addWidget(self.btn_new)

        self.btn_save = QPushButton(parent=self.topMenu)
        self.btn_save.setText("Save")
        self.btn_save.setObjectName(u"btn_save")
        self.sizePolicy.setHeightForWidth(self.btn_save.sizePolicy().hasHeightForWidth())
        self.btn_save.setSizePolicy(self.sizePolicy)
        self.btn_save.setMinimumSize(QSize(0, 45))
        self.btn_save.setFont(font)
        self.btn_save.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_save.setLayoutDirection(Qt.LeftToRight)

        right_slash = '\\'
        self.btn_save.setStyleSheet(rf"background-image: url({icons['cil-save.png'].replace(right_slash, '/')});")
        self.topMenuLayout.addWidget(self.btn_save)

        self.btn_exit = QPushButton(parent=self.topMenu)
        self.btn_exit.setText("Exit")
        self.btn_exit.setObjectName(u"btn_exit")
        self.sizePolicy.setHeightForWidth(self.btn_exit.sizePolicy().hasHeightForWidth())
        self.btn_exit.setSizePolicy(self.sizePolicy)
        self.btn_exit.setMinimumSize(QSize(0, 45))
        self.btn_exit.setFont(font)
        self.btn_exit.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_exit.setLayoutDirection(Qt.LeftToRight)

        right_slash = '\\'
        self.btn_exit.setStyleSheet(rf"background-image: url({icons['cil-x.png'].replace(right_slash, '/')});")
        self.topMenuLayout.addWidget(self.btn_exit)

        self.verticalMenuLayout.addWidget(self.topMenu, 0, Qt.AlignTop)

        # 底部菜单
        self.bottomMenu = QFrame(self)
        self.bottomMenu.setObjectName(u"bottomMenu")
        self.bottomMenu.setFrameShape(QFrame.NoFrame)
        self.bottomMenu.setFrameShadow(QFrame.Raised)
        self.bottomMenu.setStyleSheet(
            rf"""
            #bottomMenu .QPushButton {{
                background-position: left center;
                background-repeat: no-repeat;
                border: none;
                border-left: 20px solid transparent;
                background-color:transparent;
                text-align: left;
                padding-left: 44px;
            }}
            #bottomMenu .QPushButton:hover {{
                background-color: rgb(40, 44, 52);
            }}
            #bottomMenu .QPushButton:pressed {{
                background-color: rgb(189, 147, 249);
                color: rgb(255, 255, 255);
            }}
            """
        )
        # 底部菜单Layout
        self.bottomMenuLayout = QVBoxLayout(self.bottomMenu)
        self.bottomMenuLayout.setSpacing(0)
        self.bottomMenuLayout.setObjectName(u"bottomMenuLayout")
        self.bottomMenuLayout.setContentsMargins(0, 0, 0, 0)

        self.toggleLeftBox = QPushButton(parent=self.bottomMenu)
        self.toggleLeftBox.setText("Left Box")
        self.toggleLeftBox.setObjectName(u"toggleLeftBox")
        self.sizePolicy.setHeightForWidth(self.toggleLeftBox.sizePolicy().hasHeightForWidth())
        self.toggleLeftBox.setSizePolicy(self.sizePolicy)
        self.toggleLeftBox.setMinimumSize(QSize(0, 45))
        self.toggleLeftBox.setFont(font)
        self.toggleLeftBox.setCursor(QCursor(Qt.PointingHandCursor))
        self.toggleLeftBox.setLayoutDirection(Qt.LeftToRight)

        right_slash = '\\'
        self.toggleLeftBox.setStyleSheet(
            rf"background-image: url({icons['icon_settings.png'].replace(right_slash, '/')});")
        self.bottomMenuLayout.addWidget(self.toggleLeftBox)

        self.verticalMenuLayout.addWidget(self.bottomMenu, 0, Qt.AlignBottom)


if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = CLeftMenuFrame()
    MTheme('dark').apply(demo_widget)
    # 显示窗口
    demo_widget.show()
    with loop:
        loop.run_forever()
