import asyncio
import logging
import time

from PySide6 import QtCore
from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout
from qasync import QEventLoop


from framework.widgets.dayu_widgets import MTheme, dayu_theme
from framework.widgets.dayu_widgets.field_mixin import MFieldMixin
from framework.widgets.dayu_widgets.line_tab_widget import MLineTabWidget
from framework.widgets.dayu_widgets.qt import MIcon
from modules.zhihu.interfaces.cockpit_interface import CockpitInterface
from modules.zhihu.interfaces.account_interface import AccountInterface
from modules.zhihu.interfaces.hot_topic_interface import HotTopicsInterface
from modules.zhihu.interfaces.task_plan_interface import TaskPlanInterface
from modules.zhihu.interfaces.task_setting_interface import TaskSettingInterface

from modules.zhihu.icons import icons


class ZhiHuMainInterface(QWidget, MFieldMixin):
    def __init__(self, parent=None):
        super(ZhiHuMainInterface, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('知乎')
        self.setWindowIcon(MIcon(icons['知乎 (1).svg']))
        # 布局
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # 主页
        self.cockpit_interface = CockpitInterface()
        # 用户管理
        self.account_interface = AccountInterface()
        # 任务管理
        self.task_plan_interface = TaskPlanInterface()
        # 配置管理
        self.task_setting_interface = TaskSettingInterface()
        # 热点管理
        self.hot_topics_interface = HotTopicsInterface()

        # 导航条
        self.tab_center = MLineTabWidget(alignment=QtCore.Qt.AlignLeft)
        self.tab_center.set_dayu_size(dayu_theme.medium)

        self.tab_center.add_tab(self.cockpit_interface, {"text": "驾驶舱", "svg": icons["驾驶舱.svg"]})
        self.tab_center.add_tab(self.account_interface, {"text": "账户管理", "svg": icons["用户管理.svg"]})
        self.tab_center.add_tab(self.task_plan_interface, {"text": "任务管理", "svg": icons["任务管理.svg"]})
        self.tab_center.add_tab(self.hot_topics_interface, {"text": "热点管理", "svg": icons["热点.svg"]})
        self.tab_center.add_tab(self.task_setting_interface, {"text": "设置", "svg": 'alert_line.svg'})
        self.tab_center.tool_button_group.set_dayu_checked(0)

        self.main_layout.addWidget(self.tab_center)
        self.main_layout.addStretch()

    async def auto_do(self):
        """
        自动执行任务管理
        1.生成今日任务
        2.执行任务
        """
        logging.info(f"开始执行知乎任务")
        # 记录开始时间
        start_time = time.time()
        logging.info(f"开始生成任务")
        await AccountInterface.generate_account_list_task_api()
        logging.info(f"开始执行任务")
        await TaskPlanInterface.run_all_task_api()
        # 记录结束时间
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"知乎整体任务执行结束；耗时: {elapsed_time:.3f} 秒")


if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = ZhiHuMainInterface()
    # 显示窗口
    demo_widget.show()
    loop.run_forever()
    pass
