import asyncio
import sys

from PySide6 import QtAsyncio
from PySide6.QtCore import QTime
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout

from cocos_widgets.c_collapse import CCollapseWidget
from dayu_widgets import MSwitch, MTimeEdit, MTheme


class SettingsCollapse(CCollapseWidget):
    def __init__(self, parent=None):
        super(SettingsCollapse, self).__init__(parent)
        section_list = [
            {"title": "程序开机自启", "expand": False, "closable": False, "widget": QWidget()},
            {"title": "Windows 定时开机时间", "expand": False, "closable": False,
             "widget": QWidget()},
            {"title": "Windows 定时关机时间", "expand": False, "closable": False,
             "widget": QWidget()},
            {"title": "定时启动当前程序", "expand": False, "closable": False,
             "widget": QWidget()},
        ]
        self.set_section_list(section_list)
        self.m_collapse._main_layout.addStretch()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = SettingsCollapse()
    MTheme().apply(demo_widget)
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
