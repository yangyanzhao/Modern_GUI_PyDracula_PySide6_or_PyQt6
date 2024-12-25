import sys

from PySide6 import QtAsyncio
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QHeaderView, QApplication, QPushButton

from framework.app_functions import AppFunctions
from framework.app_settings import Settings
from framework.demo_interfaces.demo_home_interface import DemoHomeInterface
from framework.demo_interfaces.demo_new_page_interface import DemoNewPageInterface
from framework.ui_functions import UIFunctions
from framework.ui_main import Ui_MainWindow

from resources.framework.icons import icons
from widgets import *

os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_interfaces()  # 初始化界面
        self.init_menu()  # 初始化菜单
        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "PyDracula - Modern GUI"
        description = "PyDracula APP - Theme with colors based on Dracula for Python."
        # APPLY TEXTS
        self.setWindowTitle(title)
        self.ui.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        self.ui.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS
        self.ui.btn_home.clicked.connect(self.buttonClick)
        self.ui.btn_widgets.clicked.connect(self.buttonClick)
        self.ui.btn_new.clicked.connect(self.buttonClick)
        self.ui.btn_save.clicked.connect(self.buttonClick)

        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)

        self.ui.toggleLeftBox.clicked.connect(openCloseLeftBox)
        self.ui.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)

        self.ui.settingsTopBtn.clicked.connect(openCloseRightBox)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # 是否自定义主题
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = False
        # 自定义给主题QSS文件
        themeFile = r"themes\py_dracula_light.qss"

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            UIFunctions.theme(self, themeFile, True)

            # SET HACKS
            AppFunctions.setThemeHack(self)

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        self.ui.stackedWidget.setCurrentWidget(self.ui.demo_home_interface)
        self.ui.btn_home.setStyleSheet(UIFunctions.selectMenu(self.ui.btn_home.styleSheet()))

    # 监听缩放事件
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # 监听点击事件
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPosition()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')

    # 按钮点击事件
    # 在这里发布点击按钮的功能
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        """
        按钮导航
        :return:
        """
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # SHOW HOME PAGE
        if btnName == "btn_home":
            self.ui.stackedWidget.setCurrentWidget(self.ui.demo_home_interface)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        if btnName == "btn_widgets":
            self.ui.stackedWidget.setCurrentWidget(self.ui.widgets)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW NEW PAGE
        if btnName == "btn_new":
            self.ui.stackedWidget.setCurrentWidget(self.ui.demo_home_interface)  # SET PAGE
            UIFunctions.resetStyle(self, btnName)  # 重置所选的其他按钮的样式
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # 设置所选按钮的样式

        if btnName == "btn_save":
            print("Save BTN clicked!")

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')

    def init_menu(self):
        """
        菜单初始化
        :return:
        """
        menus_list = [
            {
                "btn_icon": icons["知乎.svg"],  # 图标
                "btn_id": "btn_zhihu",  # 按钮ID
                "btn_text": "ZhiHu",  # 按钮文本
                "btn_tooltip": "ZhiHu Page",  # 提示
                "show_top": True,  # 是否显示在顶部
                "is_active": False,  # 是否激活
                "interface": self.ui.zhihu_main_interface
            }
        ]
        UIFunctions.add_menus(self, self.ui, menus_list=menus_list)

    def init_interfaces(self):
        """
        界面初始化
        :return:
        """
        self.ui.demo_home_interface = DemoHomeInterface(parent=self)
        self.ui.demo_new_page_interface = DemoNewPageInterface(parent=self)
        self.ui.zhihu_main_interface = DemoNewPageInterface(parent=self)
        self.ui.stackedWidget.addWidget(self.ui.demo_home_interface)
        self.ui.stackedWidget.addWidget(self.ui.demo_new_page_interface)
        self.ui.stackedWidget.addWidget(self.ui.zhihu_main_interface)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    # 显示窗口
    QtAsyncio.run(handle_sigint=True)
