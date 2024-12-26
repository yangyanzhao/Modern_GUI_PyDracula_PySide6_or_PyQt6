import asyncio
import logging
import os

from PySide2.QtWidgets import QApplication
from qasync import QEventLoop
from dayu_widgets import MTheme, MPushButton
from tinydb import TinyDB

from db.tiny_db import current_directory
from gui.utils.tinydb_util import build_query, build_sort_key
from gui.widgets.c_table_view_widget.table_view_widget import TableViewWidgetAbstract, ColumnConfig

"""
增删改查窗口封装控件,tinydb快捷版
"""


class TableViewWidgetTinyDBAbstract(TableViewWidgetAbstract):
    def get_database_name(self) -> str:
        """
        返回数据库名称
        """
        raise NotImplementedError

    def get_table_name(self) -> str:
        """
        返回表名称
        """
        raise NotImplementedError

    def update_api(self, data, id) -> bool:
        self._get_orm_().update(data, doc_ids=[id])
        return True

    def delete_api(self, id_list: list) -> bool:
        self._get_orm_().remove(doc_ids=id_list)
        return True

    def insert_api(self, data=None) -> bool:
        default_data = self._get_default_data_()
        self._get_orm_().insert(default_data)
        return True

    def select_api(self, page_number, page_size, conditions: dict = None, orderby_list=None) -> (int, list[dict]):
        """
        conditions:条件字典，格式：{field:{field:field,value:value,op:op}}。field为字段名，value为条件值，op为查询方式【op为模糊，eq为精确查询，bt为范围查询（value_0,value_1）,in为包含查询（values:list）......】：[{'field':'command','value':'ASBC','op':'ct'}]
        orderby_list:排序列表,field为字段名，value为排序值【'asc','desc'】：[{'field':'command','value':'asc'}]
        """
        if conditions is None:
            conditions = {}
        if orderby_list is None:
            orderby_list = []
        # 计算起始索引
        start_index = (page_number - 1) * page_size
        condition = []
        if conditions:
            for field, values in conditions.items():
                condition.append({'field': field, **values})
        # 构建查询条件
        query = build_query(condition)
        # 执行查询
        if query is not None:
            query_results = self._get_orm_().search(query)
        else:
            query_results = self._get_orm_().all()
        # 多字段排序
        sort_key = build_sort_key(orderby_list)
        if sort_key is not None:
            sorted_result = sorted(query_results, key=sort_key)
        else:
            sorted_result = query_results
        # limit数据
        limit_result = sorted_result[start_index:start_index + page_size]
        # 由于tinydb没有id字段，只有外部的doc_id字段，这里我们主观的加入id字段
        data_list = [{'id': doc.doc_id, **doc} for doc in limit_result]
        return len(sorted_result), data_list

    def _get_orm_(self):
        if (not hasattr(self, 'orm')) or self.orm is None:
            # 数据库名称
            database_name = self.get_database_name()
            if not database_name.endswith('.json'):
                database_name = database_name + '.json'
            # 表名称
            table_name = self.get_table_name()
            # 数据库句柄
            TINY_DB_ZHIHU = TinyDB(path=os.path.join(current_directory, database_name), ensure_ascii=False,
                                   encoding='utf-8')
            self.orm = TINY_DB_ZHIHU.table(table_name)
        return self.orm

    @staticmethod
    def get_tinydb_orm(database_name, table_name):
        # 数据库句柄
        if not database_name.endswith('.json'):
            database_name = database_name + '.json'
        TINY_DB_ZHIHU = TinyDB(path=os.path.join(current_directory, database_name), ensure_ascii=False,
                               encoding='utf-8')
        orm = TINY_DB_ZHIHU.table(table_name)
        return orm


class DemoInterface(TableViewWidgetTinyDBAbstract):

    def get_table_name(self) -> str:
        return 'user'

    def get_database_name(self) -> str:
        return 'spring_boot'

    def get_header_domain_list(self):
        return [
            ColumnConfig(
                label="名称",
                key="name",
                default_value=""
            ),
            ColumnConfig(
                label="年龄",
                key="age",
                default_value=1,
                display=lambda x, y: f"{x}岁",
                color=lambda x, y: 'green' if x < 20 else 'red'
            ),
            ColumnConfig(
                label="地址",
                key="address",
                default_value=""
            )
        ]

    def get_function_button(self) -> list:
        return [
            {"text": "DEMO按鈕",
             # "icon": MIcon(icons['API输出.svg'], "#4CAF50"),
             'dayu_type': MPushButton.DefaultType,
             'clicked': lambda: print(1)
             }
        ]


if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = DemoInterface()
    MTheme(theme='dark').apply(demo_widget)
    # 显示窗口
    demo_widget.show()
    loop.run_forever()
