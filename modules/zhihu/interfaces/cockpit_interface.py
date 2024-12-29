import asyncio
import logging

from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout
from qasync import QEventLoop

from framework.widgets.cocos_widgets.c_splash_screen.c_splash_screen import increase_counter
from framework.widgets.dayu_widgets import MTheme
from framework.widgets.dayu_widgets.field_mixin import MFieldMixin
from framework.widgets.dayu_widgets.qt import MIcon
from modules.zhihu.icons import icons

"""
驾驶舱
"""


class CockpitInterface(QWidget, MFieldMixin):
    def __init__(self, parent=None):
        increase_counter("知乎驾驶舱初始化...")

        super(CockpitInterface, self).__init__(parent)
        # 初始化UI
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('知乎')
        self.setWindowIcon(MIcon(icons['知乎 (1).svg']))
        # 布局
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.sub_layout_button = QHBoxLayout()
        self.sub_layout_list = QVBoxLayout()
        self.main_layout.addLayout(self.sub_layout_button)
        self.main_layout.addLayout(self.sub_layout_list)


if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = CockpitInterface()
    # 显示窗口
    demo_widget.show()
    loop.run_forever()
