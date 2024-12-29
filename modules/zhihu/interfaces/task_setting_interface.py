import asyncio
import logging

from PySide6.QtWidgets import QApplication
from qasync import QEventLoop


from db.mysql.mysql_jdbc import select_list_by_database_table
from framework.widgets.cocos_widgets.c_splash_screen.c_splash_screen import increase_counter
from framework.widgets.cocos_widgets.c_table_view_widget.table_view_mysql_widget import TableViewWidgetMySQLAbstract
from framework.widgets.cocos_widgets.c_table_view_widget.table_view_widget import ColumnConfig
from framework.widgets.dayu_widgets import MTheme

"""
任务配置管理
"""


class TaskSettingInterface(TableViewWidgetMySQLAbstract):
    DATABASE_NAME = "zhihu"
    TABLE_NAME = "task_setting"

    def __init__(self, parent=None):
        increase_counter("知乎任务配置初始化...")

        super(TaskSettingInterface, self).__init__(parent)

    def get_database_name(self) -> str:
        return TaskSettingInterface.DATABASE_NAME

    def get_table_name(self) -> str:
        return TaskSettingInterface.TABLE_NAME

    def get_header_domain_list(self) -> list[ColumnConfig]:
        # 查出账号信息和配置信息
        accounts = select_list_by_database_table(database_name='zhihu', table_name='account',
                                                 conditions=[{'field': 'status', 'value': 1, 'op': 'eq'}])
        account_selectable = []
        self.account_mapping = {}
        for i in accounts:
            self.account_mapping[i['id']] = i['account_name']
            account_selectable.append({'label': i['account_name'], 'value': i['id']})
        self.status_mapping = {1: '启用', 0: '禁用'}
        return [
            ColumnConfig(label='账号', key='account_id', default_value=0, selectable=True,
                         selectable_list=account_selectable,
                         display=lambda x, y: self.account_mapping[x] if x in self.account_mapping else x),
            ColumnConfig(label='推荐', key='post_answers_recommend', default_value=0, searchable=False, width=40),
            ColumnConfig(label='擅长', key='post_answers_good_at', default_value=0, searchable=False, width=40),
            ColumnConfig(label='邀请', key='post_answers_invited', default_value=0, searchable=False, width=40),
            ColumnConfig(label='消息', key='post_answers_message_invitation', default_value=0, searchable=False,
                         width=40),
            ColumnConfig(label='最新', key='post_answers_new', default_value=0, searchable=False, width=40),
            ColumnConfig(label='种草', key='post_answers_mcn', default_value=0, searchable=False, width=40),
            ColumnConfig(label='擅稿', key='draft_post_answers_good_at', default_value=0, searchable=False, width=40),
            ColumnConfig(label='文章', key='publish_article', default_value=0, searchable=False, width=40),
            ColumnConfig(label='草稿', key='draft_publish_article', default_value=0, searchable=False, width=40),
            ColumnConfig(label='想法', key='publish_ideas', default_value=0, searchable=False, width=40),
            ColumnConfig(label='提问', key='asking_questions', default_value=0, searchable=False, width=40),
            ColumnConfig(label='关注', key='follow', default_value=0, searchable=False, width=40),
            ColumnConfig(label='推关', key='follow_recommend', default_value=0, searchable=False, width=40),
            ColumnConfig(label='互赞', key='refresh_likes', default_value=0, searchable=False, width=40),
            ColumnConfig(label='漫游', key='random_browsing', default_value=0, searchable=False, width=40),
            ColumnConfig(label='状态', key='status', default_value=0, selectable=True,
                         selectable_list=[{'label': v, 'value': k} for k, v in self.status_mapping.items()],
                         display=lambda x, y: self.status_mapping[x] if x in self.status_mapping else x,
                         width=60),
        ]

    def get_function_button(self) -> list:
        return []


if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = TaskSettingInterface()
    # 显示窗口
    demo_widget.show()
    loop.run_forever()
