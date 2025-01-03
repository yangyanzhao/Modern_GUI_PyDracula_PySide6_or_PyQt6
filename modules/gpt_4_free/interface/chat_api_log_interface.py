import asyncio
import datetime
import logging
import os
from PySide6.QtWidgets import QApplication

from qasync import QEventLoop

from framework.widgets.cocos_widgets.c_table_view_widget.table_view_mysql_widget import TableViewWidgetMySQLAbstract
from framework.widgets.cocos_widgets.c_table_view_widget.table_view_widget import ColumnConfig
from framework.widgets.dayu_widgets.push_button import MPushButton
from framework.widgets.dayu_widgets.qt import MIcon
from modules.gpt_4_free.icons import icons
from modules.gpt_4_free.interface.chat_interface import llm_mapping

"""
ChatAPILog日志管理
"""


class ChatAPILogInterface(TableViewWidgetMySQLAbstract):
    DATABASE_NAME = "gpt_4_free"
    TABLE_NAME = "chat_api_log"

    def __init__(self, parent=None):
        super(ChatAPILogInterface, self).__init__(parent)

    def get_database_name(self) -> str:
        return ChatAPILogInterface.DATABASE_NAME

    def get_table_name(self) -> str:
        return ChatAPILogInterface.TABLE_NAME

    def get_header_domain_list(self):
        self.status_mapping = {1: '正常', 2: '未抵达', 3: '请求失败'}
        return [
            ColumnConfig(label="模型", key="model", default_value='',
                         selectable=True, selectable_list=[i.__name__ for i in list(llm_mapping.values())],
                         editable=False, op='eq'),
            ColumnConfig(label="提示词", key="prompt", default_value='',
                         searchable=False, editable=False, op='ct'),
            ColumnConfig(label="原始回答", key="raw_answer", default_value='',
                         editable=False, op='ct'),
            ColumnConfig(label="处理后回答", key="handle_answer", default_value='',
                         searchable=False, editable=False, op='ct'),
            ColumnConfig(label="状态", key="status", default_value=1,
                         selectable=True,
                         selectable_list=[{'label': v, 'value': k} for k, v in self.status_mapping.items()],
                         editable=False,
                         display=lambda x, y: self.status_mapping[x] if x in self.status_mapping else x),
            ColumnConfig(label="耗时(秒)", key="elapsed_time", default_value=0.01,
                         searchable=False, editable=False),
            ColumnConfig(label="错误信息", key="error", default_value='',
                         searchable=False, editable=False),
            ColumnConfig(label="日期", key="date", default_value=datetime.datetime.now().strftime("%Y-%m-%d"),
                         editable=False, op='eq'),
            ColumnConfig(label="时间", key="datetime",
                         default_value=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         searchable=False, editable=False),
            ColumnConfig(label="创建时间", key="created_at",
                         default_value=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         searchable=False, editable=False),
            ColumnConfig(label="更新时间", key="updated_at",
                         default_value=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         searchable=False, editable=False),
            ColumnConfig(label="问题", key="question", default_value='',
                         searchable=False, editable=False),
        ]

    def get_function_button(self) -> list:
        return [
            {"text": "重新执行",
             "icon": MIcon(icons['API输出.svg'], "#4CAF50"),
             'dayu_type': MPushButton.DefaultType,
             'clicked': lambda: print(1)
             }
        ]


if __name__ == '__main__':
    os.environ['QT_API'] = 'PySide6'
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = ChatAPILogInterface()
    # 显示窗口
    demo_widget.show()
    loop.run_forever()
