import asyncio
import functools
import logging

from PySide2.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QListView
from dayu_widgets.qt import MIcon
from qasync import QEventLoop
from dayu_widgets import MTheme, MListView, MPushButtonGroup, MPushButton, MLineEdit, \
    MFieldMixin, MLoadingWrapper, dayu_theme, MToolButton

from db.pickle_db.data_storage_service import data_session_storage_py_one_dark
from gui.uis.windows.startup_window.main import SplashScreen, increase_counter
from modules.zhihu_auto.icons import icons

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
    demo_widget = SplashScreen(CockpitInterface)
    MTheme(theme='dark').apply(demo_widget)
    # 显示窗口
    demo_widget.show()
    loop.run_forever()
