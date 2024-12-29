import asyncio
import logging

from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

from db.mysql.mysql_jdbc import create_pool, select_list, select_list_by_database_table, select_by_id_by_database_table
from framework.widgets.cocos_widgets.c_dialog.c_confirm_dialog import CMessageDialog, CConfirmDialog
from framework.widgets.cocos_widgets.c_splash_screen.c_splash_screen import increase_counter
from framework.widgets.cocos_widgets.c_table_view_widget.table_view_mysql_widget import TableViewWidgetMySQLAbstract
from framework.widgets.cocos_widgets.c_table_view_widget.table_view_widget import ColumnConfig
from framework.widgets.dayu_widgets import MTheme
from framework.widgets.dayu_widgets.push_button import MPushButton
from framework.widgets.dayu_widgets.qt import MIcon
from modules.zhihu.api.functions.zhihu_operation import generate_plan_, generate_plans
from modules.zhihu.icons import icons

"""
账户管理
"""


class AccountInterface(TableViewWidgetMySQLAbstract):
    DATABASE_NAME = "zhihu"
    TABLE_NAME = "account"

    def __init__(self, parent=None):
        increase_counter("知乎账号初始化...")
        super(AccountInterface, self).__init__(parent)

    def get_database_name(self) -> str:
        return AccountInterface.DATABASE_NAME

    def get_table_name(self) -> str:
        return AccountInterface.TABLE_NAME

    def get_header_domain_list(self) -> list[ColumnConfig]:
        return [
            ColumnConfig(label="账号名称", key="account_name", default_value='',
                         icon=MIcon(icons["账号.svg"]), op='ct'),
            ColumnConfig(label="手机号码(账号)", key="username", default_value='',
                         icon=MIcon(icons["手机.svg"]), searchable=False),
            ColumnConfig(label="数据路径", key="user_data_dir_path", default_value='',
                         icon=MIcon(icons["路径.svg"]), searchable=False),
            ColumnConfig(label="代理端口", key="remote_debugging_port", default_value=0,
                         icon=MIcon(icons["代理端口.svg"]), searchable=False),
            ColumnConfig(label="浏览器类型", key="browser_type", default_value='chrome.exe',
                         selectable=True, selectable_list=["chrome.exe", "msedge.exe"],
                         icon=MIcon(icons["浏览器.svg"]), searchable=False),
            ColumnConfig(label="主页地址", key="home_url", default_value='',
                         icon=MIcon(icons["主页.svg"]), searchable=False),
            ColumnConfig(label="状态", key="status", default_value=1,
                         selectable=True,
                         selectable_list=[{"label": "启用", "value": 1}, {"label": "禁用", "value": 2}],
                         icon=MIcon(icons["状态.svg"]),
                         display=lambda x, y: f"启用" if x == 1 else "禁用",
                         color=lambda x, y: 'green' if x == 1 else 'red'),
            ColumnConfig(label="账号等级", key="account_level", default_value=0,
                         icon=MIcon(icons["等级.svg"]), searchable=False),
            ColumnConfig(label="Email", key="email", default_value='',
                         icon=MIcon(icons["email.svg"]), searchable=False),
            ColumnConfig(label="备注", key="remark", default_value='',
                         icon=MIcon(icons["备注.svg"]), searchable=False),
            ColumnConfig(label="命令", key="command", default_value='',
                         icon=MIcon(icons["命令.svg"]), searchable=False)
        ]

    def get_function_button(self) -> list:
        return [
            {"text": "生成任务",
             "icon": MIcon(icons['账号.svg'], "#4CAF50"),
             'dayu_type': MPushButton.DefaultType,
             'clicked': self.generate_account_task
             },
            {"text": "生成所有账号任务",
             "icon": MIcon(icons['账号.svg'], "#4CAF50"),
             'dayu_type': MPushButton.DefaultType,
             'clicked': self.generate_account_list_task
             },
            {"text": "重置任务",
             "icon": MIcon(icons['账号.svg'], "#4CAF50"),
             'dayu_type': MPushButton.DefaultType,
             'clicked': self.reset_account_task
             },
            {"text": "重置所有账号任务",
             "icon": MIcon(icons['账号.svg'], "#4CAF50"),
             'dayu_type': MPushButton.DefaultType,
             'clicked': self.reset_account_list_task
             }
        ]

    def generate_account_task(self):
        """
        生成账号任务
        """
        data_list = self.table_model.get_data_list()

        checked_doc_ids = [data['id'] for data in data_list if data.get("id_checked", 0) == 2]
        if len(checked_doc_ids) == 0:
            CMessageDialog.error("Please select the data first.", parent=self)
            return
        if len(checked_doc_ids) > 1:
            CMessageDialog.error("Only one item is allowed to be selected.", parent=self)
            return
        confirm = CConfirmDialog(title="生成任务",
                                 content="您确定要生成任务吗？",
                                 parent=self)
        exec_ = confirm.exec_()
        if exec_ == 1:
            # 查出账号信息和配置信息
            account = select_by_id_by_database_table(database_name='zhihu', table_name='account', id=checked_doc_ids[0])
            task_setting_list = select_list_by_database_table(database_name='zhihu', table_name='task_setting',
                                                              conditions=[{'field': 'status', 'value': 1, 'op': 'eq'}])
            loop = asyncio.get_running_loop()
            asyncio.run_coroutine_threadsafe(generate_plan_(account=account, task_setting_list=task_setting_list), loop)
        else:
            return

    def generate_account_list_task(self):
        """
        生成所有账号任务
        """

        confirm = CConfirmDialog(title="生成所有账号任务",
                                 content="您确定要生成所有账号任务吗？",
                                 parent=self)
        exec_ = confirm.exec_()
        if exec_ == 1:
            # 查出账号信息和配置信息
            accounts = select_list_by_database_table(database_name='zhihu', table_name='account',
                                                     conditions=[{'field': 'status', 'value': 1, 'op': 'eq'}])
            task_setting_list = select_list_by_database_table(database_name='zhihu', table_name='task_setting',
                                                              conditions=[{'field': 'status', 'value': 1, 'op': 'eq'}])
            task_setting_list_mapping = {}
            for task_setting in task_setting_list:
                if task_setting['account_id'] in task_setting_list_mapping:
                    task_setting_list_mapping[task_setting['account_id']].append(task_setting)
                else:
                    task_setting_list_mapping[task_setting['account_id']] = [task_setting]
            loop = asyncio.get_running_loop()

            asyncio.run_coroutine_threadsafe(
                generate_plans(accounts=accounts, task_setting_list_mapping=task_setting_list_mapping), loop)
        else:
            return

    def reset_account_task(self):
        """
        重置账号任务
        """
        data_list = self.table_model.get_data_list()

        checked_doc_ids = [data['id'] for data in data_list if data.get("id_checked", 0) == 2]
        if len(checked_doc_ids) == 0:
            CMessageDialog.error("Please select the data first.", parent=self)
            return
        if len(checked_doc_ids) > 1:
            CMessageDialog.error("Only one item is allowed to be selected.", parent=self)
            return
        confirm = CConfirmDialog(title="重置账号任务",
                                 content="您确定要重置账号任务吗？",
                                 parent=self)
        exec_ = confirm.exec_()
        if exec_ == 1:
            loop = asyncio.get_running_loop()
            asyncio.run_coroutine_threadsafe(generate_plan_(checked_doc_ids[0], is_reset=True), loop)
        else:
            return

    def reset_account_list_task(self):
        """
        重置所有账号任务
        """

        confirm = CConfirmDialog(title="重置所有账号任务",
                                 content="您确定要重置所有账号任务吗？",
                                 parent=self)
        exec_ = confirm.exec_()
        if exec_ == 1:
            loop = asyncio.get_running_loop()
            asyncio.run_coroutine_threadsafe(generate_plans(is_reset=True), loop)
        else:
            return

    @staticmethod
    async def generate_account_list_task_api():
        """
        生成所有账号任务
        """
        # 查出所有账号和账号配置
        pool = await create_pool(db='zhihu')
        accounts = await select_list(pool=pool, table_name='account',
                                     condition=[{'field': 'status', 'value': 1, 'op': 'eq'}])
        task_setting_list = select_list_by_database_table(database_name='zhihu', table_name='task_setting',
                                                          conditions=[{'field': 'status', 'value': 1, 'op': 'eq'}])
        task_setting_list_mapping = {}
        for task_setting in task_setting_list:
            if task_setting['account_id'] in task_setting_list_mapping:
                task_setting_list_mapping[task_setting['account_id']].append(task_setting)
            else:
                task_setting_list_mapping[task_setting['account_id']] = [task_setting]
        # loop = asyncio.get_running_loop()
        #
        # asyncio.run_coroutine_threadsafe(
        #     generate_plans(accounts=accounts, task_setting_list_mapping=task_setting_list_mapping), loop)
        await generate_plans(accounts=accounts, task_setting_list_mapping=task_setting_list_mapping)



if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = AccountInterface()
    # 显示窗口
    demo_widget.show()
    loop.run_forever()
    pass
