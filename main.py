import asyncio
import logging
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, \
    QStackedWidget, QMainWindow, QApplication
from qasync import QEventLoop

from framework.app_settings import Settings
from framework.interfaces.home_interface import HomeInterface
from framework.ui_functions import UIFunctions
from framework.widgets.cocos_widgets.c_bottom_bar import CBottomBar
from framework.widgets.cocos_widgets.c_content_top_bg import CContentTopBg
from framework.widgets.cocos_widgets.c_extra_left_box import CExtraLeftBox
from framework.widgets.cocos_widgets.c_extra_right_box import CExtraRightBox
from framework.widgets.cocos_widgets.c_left_menu_bg import CLeftMenuBg
from framework.widgets.dayu_widgets import MTheme
from resources.framework.icons import icons
from modules.zhihu.zhihu_main_interface import ZhiHuMainInterface


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        # 初始化UI
        self.setupUi()
        self.init_menu()  # 初始化菜单
        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # SET UI DEFINITIONS
        UIFunctions.uiDefinitions(self)

        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)

        self.leftMenuBg.leftMenuFrame.toggleLeftBox.clicked.connect(openCloseLeftBox)
        self.extraLeftBox.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)

        self.contentTopBg.rightButtons.settingsTopBtn.clicked.connect(openCloseRightBox)

        self.show()

    def setupUi(self):
        self.setObjectName(u"MainWindow")
        self.resize(1280, 720)
        self.setMinimumSize(QSize(940, 560))
        self.styleSheet = QWidget(self)
        self.styleSheet.setObjectName(u"styleSheet")

        font = QFont()
        font.setFamily(u"Segoe UI")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        self.styleSheet.setFont(font)
        self.appMargins = QVBoxLayout(self.styleSheet)
        self.appMargins.setSpacing(0)
        self.appMargins.setObjectName(u"appMargins")
        self.appMargins.setContentsMargins(0, 0, 0, 0)

        # 背景
        self.bgApp = QFrame(self.styleSheet)
        self.bgApp.setObjectName(u"bgApp")
        self.bgApp.setFrameShape(QFrame.NoFrame)
        self.bgApp.setFrameShadow(QFrame.Raised)
        self.appLayout = QHBoxLayout(self.bgApp)
        self.appLayout.setSpacing(0)
        self.appLayout.setObjectName(u"appLayout")
        self.appLayout.setContentsMargins(0, 0, 0, 0)

        # 左侧菜单
        self.leftMenuBg = CLeftMenuBg(self.bgApp)
        self.appLayout.addWidget(self.leftMenuBg)

        # 左侧扩展界面
        self.extraLeftBox = CExtraLeftBox(self.bgApp)

        self.appLayout.addWidget(self.extraLeftBox)

        # 内容盒子
        self.contentBox = QFrame(self.bgApp)
        self.contentBox.setObjectName(u"contentBox")
        self.contentBox.setFrameShape(QFrame.NoFrame)
        self.contentBox.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.contentBox)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)

        # 右侧顶部
        self.contentTopBg = CContentTopBg(self.contentBox)
        self.verticalLayout_2.addWidget(self.contentTopBg)

        self.contentBottom = QFrame(self.contentBox)
        self.contentBottom.setObjectName(u"contentBottom")
        self.contentBottom.setFrameShape(QFrame.NoFrame)
        self.contentBottom.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.contentBottom)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)

        self.content = QFrame(self.contentBottom)
        self.content.setObjectName(u"content")
        self.content.setFrameShape(QFrame.NoFrame)
        self.content.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.content)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)

        # 页面容器
        self.pagesContainer = QFrame(self.content)
        self.pagesContainer.setObjectName(u"pagesContainer")
        self.pagesContainer.setFrameShape(QFrame.NoFrame)
        self.pagesContainer.setFrameShadow(QFrame.Raised)
        self.verticalLayout_15 = QVBoxLayout(self.pagesContainer)
        self.verticalLayout_15.setSpacing(0)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(10, 10, 10, 10)
        self.stackedWidget = QStackedWidget(self.pagesContainer)
        self.stackedWidget.setObjectName(u"stackedWidget")
        # self.stackedWidget.setStyleSheet(u"background: transparent;")

        self.verticalLayout_15.addWidget(self.stackedWidget)

        self.horizontalLayout_4.addWidget(self.pagesContainer)

        # 右侧扩展界面
        self.extraRightBox = CExtraRightBox(self.content)
        self.horizontalLayout_4.addWidget(self.extraRightBox)

        self.verticalLayout_6.addWidget(self.content)

        self.bottomBar = CBottomBar(self.contentBottom)

        self.verticalLayout_6.addWidget(self.bottomBar)

        self.verticalLayout_2.addWidget(self.contentBottom)

        self.appLayout.addWidget(self.contentBox)

        self.appMargins.addWidget(self.bgApp)

        self.setCentralWidget(self.styleSheet)

    # 监听缩放事件
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # 监听点击事件
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPosition()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')

    # 按钮点击事件
    def buttonClick(self):
        """
        按钮导航
        :return:
        """
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()
        if btnName in self.menu_interface_mapping:
            self.stackedWidget.setCurrentWidget(self.menu_interface_mapping[btnName])
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # 不知道为什么要设置两次才完全生效。。。就这么滴吧
            UIFunctions.resetStyle(self, btnName)

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')

    def init_menu(self):
        """
        菜单初始化
        :return:
        """
        menus_list = [
            {
                "btn_icon": icons["cil-home.png"],  # 图标
                "btn_id": "btn_home",  # 按钮ID
                "btn_text": "Home",  # 按钮文本
                "btn_tooltip": "Home Page",  # 提示
                "show_top": True,  # 是否显示在顶部
                "is_active": False,  # 是否激活
                "interface": HomeInterface(parent=self)
            },
            {
                "btn_icon": icons["知乎.svg"],  # 图标
                "btn_id": "btn_zhihu",  # 按钮ID
                "btn_text": "ZhiHu",  # 按钮文本
                "btn_tooltip": "ZhiHu Page",  # 提示
                "show_top": True,  # 是否显示在顶部
                "is_active": False,  # 是否激活
                "interface": ZhiHuMainInterface(parent=self)
            }
        ]

        UIFunctions.add_menus(self, menus_list=menus_list)


if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = MainWindow()
    MTheme('dark').apply(demo_widget)
    # 显示窗口
    demo_widget.show()
    with loop:
        loop.run_forever()
