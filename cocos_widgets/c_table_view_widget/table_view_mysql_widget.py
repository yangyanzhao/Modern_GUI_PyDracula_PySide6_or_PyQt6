import asyncio
import json
import logging
import sys
import traceback

from PySide6 import QtAsyncio
from PySide6.QtWidgets import QApplication

from cocos_widgets.c_table_view_widget.table_view_widget import TableViewWidgetAbstract, ColumnConfig
from dayu_widgets import MTheme, MPushButton
from db.mysql.mysql_jdbc import create_pool, close_pool, insert, delete_by_ids, update_by_id, \
    select_count, select_page, select_list, truncate_table, executor

"""
增删改查窗口封装控件,MYSQL快捷版
"""


def is_event_loop_running():
    try:
        # 尝试获取当前运行的事件循环
        loop = asyncio.get_running_loop()
        return loop is not None
    except RuntimeError:
        # 如果没有运行中的事件循环，会抛出 RuntimeError
        return False


class TableViewWidgetMySQLAbstract(TableViewWidgetAbstract):

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
            if k is not None and v is not None:
                if isinstance(v, list) or isinstance(v, dict):
                    data[k] = json.dumps(v)

        async def async_slot_function():
            # 批量
            pool = await create_pool(db=self.get_database_name())
            try:
                await update_by_id(pool=pool, table_name=self.get_table_name(), data=data)
                return True
            except:
                traceback.print_exc()
                exc_info = traceback.format_exc()
                return False
            finally:
                await close_pool(pool)

        if is_event_loop_running():
            loop = asyncio.get_running_loop()
            task = loop.create_task(async_slot_function())
            # 为任务添加回调函数
            task.add_done_callback(lambda t: self.reload_data())
        else:
            result = asyncio.run(async_slot_function())

    def delete_api(self, id_list: list):
        async def async_slot_function():
            pool = await create_pool(db=self.get_database_name())
            try:
                await delete_by_ids(pool=pool, table_name=self.get_table_name(), id_list=id_list)
                return True
            except:
                traceback.print_exc()
                exc_info = traceback.format_exc()
                return False
            finally:
                await close_pool(pool)

        if is_event_loop_running():
            loop = asyncio.get_running_loop()
            task = loop.create_task(async_slot_function())
            # 为任务添加回调函数
            task.add_done_callback(lambda t: self.reload_data())
        else:
            result = asyncio.run(async_slot_function())

    def insert_api(self, data=None):
        default_data = self._get_default_data_()
        # 这里要对data进行预处理，将list或者dict进行序列化
        for k, v in default_data.items():
            if isinstance(v, list) or isinstance(v, dict):
                default_data[k] = json.dumps(v)

        async def async_slot_function():
            pool = await create_pool(db=self.get_database_name())
            try:
                # 插入数据
                await insert(pool=pool, table_name=self.get_table_name(), data=default_data)
                return True
            except:
                traceback.print_exc()
                exc_info = traceback.format_exc()
                return False
            finally:
                await close_pool(pool)

        if is_event_loop_running():
            loop = asyncio.get_running_loop()
            task = loop.create_task(async_slot_function())
            # 为任务添加回调函数
            task.add_done_callback(lambda t: self.reload_data())
        else:
            result = asyncio.run(async_slot_function())

    def select_api(self, page_number, page_size, conditions: dict = None, orderby_list=None) -> (int, list[dict]):
        """
        conditions:条件字典，格式：{field:{field:field,value:value,op:op}}。field为字段名，value为条件值，op为查询方式【op为模糊，eq为精确查询，bt为范围查询（value_0,value_1）,in为包含查询（values:list）......】：[{'field':'command','value':'ASBC','op':'ct'}]
        orderby_list:排序列表,field为字段名，value为排序值【'asc','desc'】：[{'field':'command','value':'asc'}]
        """
        condition = []  # [{field:field,value:value,op:op},{field:field,value:value,op:op}]
        if conditions is None:
            conditions = {}
        if orderby_list is None:
            orderby_list = []
        for field, values in conditions.items():
            condition.append({'field': field, **values})

        async def async_slot_function():
            pool = await create_pool(db=self.get_database_name())
            try:
                # 查询数量
                count = await select_count(pool=pool, table_name=self.get_table_name(),
                                           condition=condition)
                page_data = await select_page(pool=pool, table_name=self.get_table_name(),
                                              condition=condition, columns=None,
                                              page=page_number, page_size=page_size,
                                              order_by=[{'field': odb[0], 'value': odb[1]} for odb in orderby_list])
                return count, page_data
            except:
                traceback.print_exc()
                exc_info = traceback.format_exc()
                return 0, []  # 确保返回一个有效的值，即使发生了错误
            finally:
                await close_pool(pool)

        # 获取或创建新的事件循环
        # count, data_list = asyncio.run(async_slot_function())
        # 使用线程池执行异步任务
        future = executor.submit(lambda: QtAsyncio.run(async_slot_function(),keep_running=False))
        try:
            data_list = future.result(timeout=5)  # 阻塞等待结果
            print(data_list)  # 打印结果
        except Exception as e:
            import traceback
            traceback.print_exc()
            exc_info = traceback.format_exc()
            count, data_list = 0, []

        # 获取异步槽函数的结果
        # 这里要对data_list进行逆向序列化
        for data in data_list:
            for k, v in data.items():
                if k.endswith('_list'):
                    try:
                        if v is not None:
                            # 尝试逆向序列化
                            data[k] = json.loads(v)
                    except:
                        traceback.print_exc()
                        exc_info = traceback.format_exc()

        return count, data_list

    def select_list(self, conditions: list[dict] = None, orderby_list=None) -> list[dict]:
        """
        conditions:条件列表，field为字段名，value为条件值，op为查询方式【op为模糊，eq为精确查询，bt为范围查询（value_0,value_1）,in为包含查询（values:list）......】：[{'field':'command','value':'ASBC','op':'ct'}]
        orderby_list:排序列表,field为字段名，value为排序值【'asc','desc'】：[{'field':'command','value':'asc'}]
        """
        condition = []
        if conditions is None:
            conditions = {}
        if orderby_list is None:
            orderby_list = []
        for field, values in conditions.items():
            condition.append({'field': field, **values})

        async def async_slot_function():
            pool = await create_pool(db=self.get_database_name())
            try:
                page_data = await select_list(pool=pool, table_name=self.get_table_name(),
                                              condition=condition, columns=None,
                                              order_by=[{'field': odb[0], 'value': odb[1]} for odb in orderby_list])
                return page_data
            except:
                traceback.print_exc()
                exc_info = traceback.format_exc()
            finally:
                await close_pool(pool)

        # 获取或创建新的事件循环
        data_list = asyncio.run(async_slot_function())

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

        return data_list

    def truncate_api(self):
        """
        截断表（清空数据）
        """

        async def async_slot_function():
            # 批量
            pool = await create_pool(db=self.get_database_name())
            try:
                await truncate_table(pool=pool, table_name=self.get_table_name())
                return True
            except:
                traceback.print_exc()
                exc_info = traceback.format_exc()
                return False
            finally:
                await close_pool(pool)

        if is_event_loop_running():
            loop = asyncio.get_running_loop()
            task = loop.create_task(async_slot_function())
            # 为任务添加回调函数
            task.add_done_callback(lambda t: self.reload_data())
        else:
            result = asyncio.run(async_slot_function())


class DemoInterface(TableViewWidgetMySQLAbstract):
    DATABASE_NAME = "user"
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


def get_header_domain_list_by_DDL(ddl: str):
    # TODO 从DDL中解析出字段信息
    pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoInterface()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
