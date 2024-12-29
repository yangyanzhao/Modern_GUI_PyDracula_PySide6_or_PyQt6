import asyncio
import json
import logging
import traceback

from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

from framework.widgets.cocos_widgets.c_table_view_widget.table_view_widget import TableViewWidgetAbstract, ColumnConfig
from framework.widgets.dayu_widgets import MTheme, MPushButton
from db.sqlite_db.sqlite3_jdbc import insert, delete_by_ids, update_by_id, \
    select_count, select_page, truncate_table

"""
增删改查窗口封装控件,SQLite3快捷版
"""


class TableViewWidgetSQLite3Abstract(TableViewWidgetAbstract):

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

    def update_api(self, data, id):
        # 这里要对data进行预处理，将list或者dict进行序列化
        for k, v in data.items():
            if isinstance(v, list) or isinstance(v, dict):
                data[k] = json.dumps(v)

        def async_slot_function():
            try:
                update_by_id(database_name=self.get_database_name(), table_name=self.get_table_name(), data=data)
                return True
            except:
                traceback.print_exc()
                exc_info = traceback.format_exc()
                return False

        async_slot_function()

    def delete_api(self, id_list: list):
        def async_slot_function():
            try:
                delete_by_ids(database_name=self.get_database_name(), table_name=self.get_table_name(), id_list=id_list)
                return True
            except:
                traceback.print_exc()
                exc_info = traceback.format_exc()
                return False

        async_slot_function()

    def insert_api(self, data=None):
        default_data = self._get_default_data_()
        # 这里要对data进行预处理，将list或者dict进行序列化
        for k, v in default_data.items():
            if isinstance(v, list) or isinstance(v, dict):
                default_data[k] = json.dumps(v)

        def async_slot_function():
            try:
                # 插入数据
                insert(database_name=self.get_database_name(), table_name=self.get_table_name(), data=default_data)
                return True
            except:
                traceback.print_exc()
                exc_info = traceback.format_exc()
                return False

        async_slot_function()

    def select_api(self, page_number, page_size, conditions=None, orderby_list=None) -> (int, list[dict]):
        """
        conditions:条件字典，格式：{field:{field:field,value:value,op:op}}。field为字段名，value为条件值，op为查询方式【op为模糊，eq为精确查询，bt为范围查询（value_0,value_1）,in为包含查询（values:list）......】：[{'field':'command','value':'ASBC','op':'ct'}]
        orderby_list:排序列表,field为字段名，value为排序值【'asc','desc'】：[{'field':'command','value':'asc'}]
        """
        condition = []
        if conditions is None:
            conditions = {}
        if orderby_list is None:
            orderby_list = []
        for field, values in conditions.items():
            condition.append({'field': field, **values})

        def async_slot_function():

            try:
                # 查询数量
                count = select_count(database_name=self.get_database_name(), table_name=self.get_table_name(),
                                     condition=condition)
                page_data = select_page(database_name=self.get_database_name(), table_name=self.get_table_name(),
                                        condition=condition, columns=None,
                                        page=page_number, page_size=page_size,
                                        order_by=[{'field': odb[0], 'value': odb[1]} for odb in orderby_list])
                return count, page_data
            except:
                traceback.print_exc()
                exc_info = traceback.format_exc()

        # 获取或创建新的事件循环
        count, data_list = async_slot_function()
        # 获取异步槽函数的结果
        # 这里要对data_list进行逆向序列化
        for data in data_list:
            for k, v in data.items():
                if k.endswith('_list'):
                    try:
                        # 尝试逆向序列化
                        data[k] = json.loads(v)
                    except:
                        traceback.print_exc()
                        exc_info = traceback.format_exc()
        return count, data_list

    def truncate_api(self):
        """
        截断表（清空数据）
        """

        def async_slot_function():
            try:
                truncate_table(database_name=self.get_database_name(), table_name=self.get_table_name())
                return True
            except:
                traceback.print_exc()
                exc_info = traceback.format_exc()
                return False

        async_slot_function()


class DemoInterface(TableViewWidgetSQLite3Abstract):
    DATABASE_NAME = "sqlite3_db"
    TABLE_NAME = "spring_boot"

    def get_database_name(self) -> str:
        return DemoInterface.DATABASE_NAME

    def get_table_name(self) -> str:
        return DemoInterface.TABLE_NAME

    def get_header_domain_list(self):
        return [
            ColumnConfig(
                label="名称",
                key="name",
                default_value="",
                op='ct'
            ),
            ColumnConfig(
                label="年龄",
                key="age",
                default_value=1,
                display=lambda x, y: f"{x}岁",
            ),
            ColumnConfig(
                label="地址",
                key="address",
                default_value="",
                op='ct'
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


def get_header_domain_list_by_DDL(ddl: str):
    # TODO 从DDL中解析出字段信息
    pass


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
    pass
