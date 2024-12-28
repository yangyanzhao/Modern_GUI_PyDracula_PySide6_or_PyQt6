import asyncio
import logging

from PySide6 import QtCore
from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout

from qasync import QEventLoop

from db.widget_pointer import widget_pointer_mapping
from framework.widgets.cocos_widgets.c_splash_screen.c_splash_screen import increase_counter
from framework.widgets.dayu_widgets import dayu_theme
from framework.widgets.dayu_widgets.field_mixin import MFieldMixin
from framework.widgets.dayu_widgets.line_tab_widget import MLineTabWidget
from modules.gpt_4_free.icons import icons
from modules.gpt_4_free.interface.chat_api_log_interface import ChatAPILogInterface
from modules.gpt_4_free.interface.chat_interface import ChatInterface
from modules.gpt_4_free.interface.images_interface import ImagesInterface


class Gpt4FreeWidget(QWidget, MFieldMixin):
    def __init__(self, parent=None):
        increase_counter("GPT窗口初始化...")
        super(Gpt4FreeWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        # 布局
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # 主页
        self.chat_interface = ChatInterface()
        widget_pointer_mapping['gpt_4_free.chat_interface'] = self.chat_interface
        self.images_interface = ImagesInterface()
        widget_pointer_mapping['gpt_4_free.images_interface'] = self.images_interface
        self.api_interface = ChatAPILogInterface()
        widget_pointer_mapping['gpt_4_free.api_interface'] = self.api_interface

        # 导航条
        self.tab_center = MLineTabWidget(alignment=QtCore.Qt.AlignLeft)
        self.tab_center.set_dayu_size(dayu_theme.medium)

        self.tab_center.add_tab(self.chat_interface, {"text": "AI对话", "svg": icons['ai对话.svg']})
        self.tab_center.add_tab(self.images_interface, {"text": "AI绘图", "svg": icons['ai绘画.svg']})
        self.tab_center.add_tab(self.api_interface, {"text": "API输出", "svg": icons['API输出.svg']})
        self.tab_center.tool_button_group.set_dayu_checked(0)

        self.main_layout.addWidget(self.tab_center)

    def auto_do(self):
        """
        自动执行任务管理
        """
        print("自动执行")


if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    wx_main_widget = Gpt4FreeWidget()
    # 显示窗口
    wx_main_widget.show()
    with loop:
        loop.run_forever()
