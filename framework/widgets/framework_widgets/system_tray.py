from framework.utils.file_lock import FileLock

import os
import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QCoreApplication, QThread, QTimer

from resources.framework.icons import icons

# from gui.core.functions import Functions

"""
最小化到系统托盘
"""


class SystemTrayTool:
    def __init__(self, widget: QWidget):
        super(SystemTrayTool, self).__init__()
        self.widget = widget
        # 创建一个系统托盘图标
        self.widget.tray_icon = QSystemTrayIcon(icon=QIcon(icons["logo.svg"]),
                                                parent=self.widget)  # 设置托盘图标，请确保 "icon.png" 存在
        self.widget.tray_icon.setToolTip("微信助手")  # 设置提示
        # 创建托盘图标的菜单
        tray_menu = QMenu(self.widget)
        restore_action = QAction("显示微信", self.widget)
        quit_action = QAction("退出微信", self.widget)
        restore_action.triggered.connect(self.widget.show)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(restore_action)
        tray_menu.addAction(quit_action)
        # 用Qss美化一下菜单
        qss_sheet = """QMenu {
            background-color: #ffffff;
            color: #303133;
            border: 1px solid #e4e7ed;
            border-radius: 4px;
            padding: 4px 0;
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            font-size: 14px;
            }
            QMenu::item {
                padding: 8px 20px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #f5f7fa;
                color: #409eff;
            }
            QMenu::separator {
                height: 1px;
                background: #e4e7ed;
                margin: 4px 0;
            }"""
        tray_menu.setStyleSheet(qss_sheet)
        # 将菜单设置为系统托盘图标的右键菜单
        self.widget.tray_icon.setContextMenu(tray_menu)

        # 显示托盘图标
        self.widget.tray_icon.show()

        # 连接托盘图标的激活信号到显示窗口的槽函数
        def on_tray_icon_activated(reason):
            # 当用户点击托盘图标时，显示主窗口
            if reason == QSystemTrayIcon.Trigger:
                print("单击托盘图标")
                self.widget.show()
            elif reason == QSystemTrayIcon.DoubleClick:
                print("双击托盘图标")
                self.widget.show()

        self.widget.tray_icon.activated.connect(on_tray_icon_activated)

        def closeEvent(event):
            # 当用户点击关闭按钮时，最小化到托盘而不是关闭程序
            self.widget.hide()  # 隐藏主窗口
            self.widget.tray_icon.showMessage("最小化到系统盘", "程序已最小化到系统托盘。",
                                              QIcon(icons["logo.svg"]), 1000)
            event.ignore()  # 忽略关闭事件

        setattr(self.widget, "closeEvent", closeEvent)

    def quit_application(self):
        # 确保所有线程和定时器被正确关闭
        print(f"关闭线程：{len(self.widget.findChildren(QThread))}")
        for thread in self.widget.findChildren(QThread):
            thread.quit()
            thread.wait()
        print(f"关闭定时任务：{len(self.widget.findChildren(QTimer))}")
        for timer in self.widget.findChildren(QTimer):
            timer.stop()
        QCoreApplication.instance().quit()
        if hasattr(self.widget, "app"):
            self.widget.app.exit()
            self.widget.app.quit()
        QApplication.quit()
        QApplication.exit()
        pid = FileLock.get_pid()
        if FileLock.is_pid_running(pid):
            print(f"杀死进程：{pid}")
            FileLock.kill_process_by_pid(pid)


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        SystemTrayTool(self)
        # 设置窗口标题和大小
        self.setGeometry(100, 100, 300, 200)

        # 创建一个按钮，用于测试最小化到托盘功能
        self.button = QLabel("Minimize to Tray", self)
        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MyWindow()
    window.show()

    sys.exit(app.exec_())
