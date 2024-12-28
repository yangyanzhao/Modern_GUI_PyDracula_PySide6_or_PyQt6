import asyncio
import datetime
import logging

from PySide6.QtWidgets import QApplication

from widgets.cocos_widgets import CMessageDialog, CConfirmDialog
from widgets.cocos_widgets.c_splash_screen import increase_counter
from widgets.cocos_widgets import TableViewWidgetMySQLAbstract
from widgets.cocos_widgets import ColumnConfig
from widgets.dayu_widgets import MIcon
from qasync import QEventLoop
from widgets.dayu_widgets import MTheme, MPushButton

from db.mysql.mysql_jdbc import select_list_by_database_table
from modules.zhihu.api.functions.zhihu_operation import start_all_task, start_one_task
from modules.zhihu.api.utils.common_utils import kill_process_by_name
from modules.zhihu.icons import icons
from utils.table_widget_util import remove_list_keys

"""
任务管理
"""

mapping = {
    1: '推荐回答',
    2: '擅长回答',
    3: '邀请回答',
    4: '消息邀请回答',
    5: '最新回答',
    6: '种草回答',
    7: '草稿回答',
    8: '文章发布',
    9: '文章草稿',
    10: '想法发布',
    11: '提问',
    12: '关注',
    13: '推荐关注',
    14: '互赞',
    15: '漫游',
}


class TaskPlanInterface(TableViewWidgetMySQLAbstract):
    DATABASE_NAME = "zhihu"
    TABLE_NAME = "task_plan"

    def __init__(self, parent=None):
        increase_counter("知乎任务计划初始化...")

        super(TaskPlanInterface, self).__init__(parent)

    def get_database_name(self) -> str:
        return TaskPlanInterface.DATABASE_NAME

    def get_table_name(self) -> str:
        return TaskPlanInterface.TABLE_NAME

    def get_header_domain_list(self) -> list[ColumnConfig]:
        # 查出账号信息和配置信息
        accounts = select_list_by_database_table(database_name='zhihu', table_name='account',
                                                 conditions=[{'field': 'status', 'value': 1, 'op': 'eq'}])

        account_selectable = []
        self.account_mapping = {}
        for i in accounts:
            self.account_mapping[i['id']] = i['account_name']
            account_selectable.append({'label': i['account_name'], 'value': i['id']})
        self.status_mapping = {0: '执行结果为None', 1: '未完成', 2: '完成', 3: '意外情况'}

        return [
            ColumnConfig(label="账号", key="account_id", default_value=0,
                         selectable=True, selectable_list=[],
                         editable=False,
                         display=lambda x, y: self.account_mapping[x] if x in self.account_mapping else x),
            ColumnConfig(label="任务类型", key="task_type", default_value=1,
                         selectable=True, selectable_list=[{'label': v, 'value': k} for k, v in mapping.items()],
                         editable=False,
                         display=lambda x, y: mapping[x] if x in mapping else x),
            ColumnConfig(label="命令", key="command", default_value='', searchable=False, editable=False),
            ColumnConfig(label="优先级", key="priority", default_value=0, searchable=False),
            ColumnConfig(label="状态", key="status", default_value=0, selectable=True,
                         selectable_list=[{'label': v, 'value': k} for k, v in self.status_mapping.items()],
                         display=lambda x, y: self.status_mapping[x] if x in self.status_mapping else x),
            ColumnConfig(label="任务日期", key="plan_date", default_value=datetime.date.today().strftime("%Y-%m-%d"),
                         editable=False),
            ColumnConfig(label="完成时间", key="finish_time", default_value="2000-01-01 00:00:00", searchable=False,
                         editable=False),
            ColumnConfig(label="创建时间", key="create_time",
                         default_value=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), searchable=False,
                         editable=False),
            ColumnConfig(label="消息", key="message", default_value='', op='ct', editable=False),
        ]

    def get_function_button(self) -> list:
        return [
            {"text": "执行任务",
             "icon": MIcon(icons['账号.svg'], "#4CAF50"),
             'dayu_type': MPushButton.DefaultType,
             'clicked': self.run_task
             },
            {"text": "执行所有任务",
             "icon": MIcon(icons['账号.svg'], "#4CAF50"),
             'dayu_type': MPushButton.DefaultType,
             'clicked': self.run_all_task
             }
        ]

    def run_task(self):
        data_list = self.table_model.get_data_list()

        checked_doc_ids = [data['id'] for data in data_list if data.get("id_checked", 0) == 2]
        checked_data = [data for data in data_list if data.get("id_checked", 0) == 2]
        if len(checked_doc_ids) == 0:
            CMessageDialog.error("Please select the data first.", parent=self)
            return
        if len(checked_doc_ids) > 1:
            CMessageDialog.error("Only one item is allowed to be selected.", parent=self)
            return
        confirm = CConfirmDialog(title="执行任务",
                                 content="您确定要执行任务吗？",
                                 parent=self)
        exec_ = confirm.exec_()
        if exec_ == 1:
            # 查出账号信息
            accounts = select_list_by_database_table(database_name='zhihu', table_name='account',
                                                     conditions=[{'field': 'status', 'value': 1, 'op': 'eq'}])
            account = None
            for a in accounts:
                if a['id'] == checked_data[0]['account_id']:
                    account = a
                    break
            # 查出任务信息
            loop = asyncio.get_running_loop()

            asyncio.run_coroutine_threadsafe(
                start_one_task(account=account, accounts=accounts, task_plan=remove_list_keys(checked_data[0]),
                               hide=False),
                loop)
        else:
            return

    def run_all_task(self):

        confirm = CConfirmDialog(title="执行所有任务",
                                 content="您确定要执行所有任务吗？",
                                 parent=self)
        exec_ = confirm.exec_()
        if exec_ == 1:
            # 关闭浏览器应用
            kill_process_by_name("chrome.exe")
            loop = asyncio.get_running_loop()
            asyncio.run_coroutine_threadsafe(start_all_task(hide=False), loop)
        else:
            return

    @staticmethod
    async def run_all_task_api():

        # 关闭浏览器应用
        kill_process_by_name("chrome.exe")
        await start_all_task(hide=True)


if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = TaskPlanInterface()
    MTheme(theme='dark').apply(demo_widget)
    # 显示窗口
    demo_widget.show()
    loop.run_forever()
    pass
