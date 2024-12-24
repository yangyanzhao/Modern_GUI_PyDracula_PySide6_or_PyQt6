# 连接到 SQLite 数据库（如果数据库不存在，会自动创建）
import os.path
import datetime
import logging
import sqlite3

from sqlite3worker import Sqlite3Worker

from db.sqlite_db import current_directory

"""
SQLite3数据库操作相关API
"""
# 数据库文件路径
# os.path.join(current_directory, f'{database_name}.db') = os.path.join(current_directory, 'sqlite3_db.db')

# 定义类型映射
type_mapping = {
    int: 'INTEGER',
    float: 'REAL',
    # str: 'VARCHAR(255)',
    str: 'TEXT',
    bool: 'BOOLEAN',
    datetime.datetime: 'DATETIME',
    datetime.date: 'DATE',
    None: 'TEXT',
}


class SQLiteWorkerContext:
    """
    自定义一个上下文管理器
    """

    def __init__(self, database):
        self.database = database
        self.worker = None

    def __enter__(self):
        # 进入上下文时创建 Sqlite3Worker 实例
        self.worker = Sqlite3Worker(self.database)
        return self.worker

    def __exit__(self, exc_type, exc_value, traceback):
        # 退出上下文时关闭数据库连接
        if self.worker:
            self.worker.close()


def create_table(database_name: str, table_name: str, data: dict):
    """
    创建表
    :param table_name: 数据库表名
    :param data: 数据字典，键为字段名，值为字段类型
    """
    with SQLiteWorkerContext(os.path.join(current_directory, f'{database_name}.db')) as db:

        # 自动添加主键 id
        columns = ['id INTEGER PRIMARY KEY']

        # 根据 data 字典中的数据类型生成字段定义
        if data:
            for key, value in data.items():
                field_type = type_mapping.get(type(value))
                if field_type:
                    columns.append(f"`{key}` {field_type}")
                elif value is None or field_type is None:
                    columns.append(f"`{key}` {'TEXT'}")
                else:
                    raise ValueError(f"Unsupported data type for field '{key}': {type(value)}")
        # 自动添加创建时间和更新时间字段
        columns.append('created_at DATETIME DEFAULT CURRENT_TIMESTAMP')
        columns.append('updated_at DATETIME DEFAULT CURRENT_TIMESTAMP')

        # 构建 SQL 创建表语句
        sql = f'''
                CREATE TABLE `{table_name}` (
                    {', '.join(columns)}
                )
            '''
        logging.info(sql)
        db.execute(sql)


def get_table_fields(database_name: str, table_name: str):
    conn = sqlite3.connect(os.path.join(current_directory, f'{database_name}.db'))
    cursor = conn.cursor()
    # 查询表结构
    cursor.execute(f"""
       PRAGMA table_info(`{table_name}`)
       """)
    # 获取查询结果
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_table(database_name: str, table_name: str, data: dict):
    """
    更新表结构
    :param table_name: 数据库表名
    :param data: 数据字典，键为字段名，值为字段类型
    """
    with SQLiteWorkerContext(os.path.join(current_directory, f'{database_name}.db')) as db:
        # 保留的字段
        reserved_fields = {'id', 'created_at', 'updated_at'}
        current_fields = get_table_fields(database_name, table_name)
        current_fields_dict = {field[1]: field[2] for field in current_fields}

        if data:
            for key, value in data.items():
                field_type = type_mapping.get(type(value))
                if field_type is None:
                    field_type = 'TEXT'
                if key not in current_fields_dict and key not in reserved_fields:
                    # 构建 SQL 更新表语句
                    sql = f'''
                                    ALTER TABLE `{table_name}`
                                    {', '.join([f"ADD COLUMN `{key}` {field_type}"])}
                                '''
                    # 执行 SQL 更新表语句
                    logging.info(sql)
                    db.execute(sql)
                elif key in current_fields_dict and current_fields_dict[
                    key] != field_type and key not in reserved_fields:
                    # 构建 SQL 更新表语句
                    sql = f'''
                                    ALTER TABLE `{table_name}`
                                    {', '.join([f"MODIFY COLUMN `{key}` {field_type}"])}
                                '''
                    # 执行 SQL 更新表语句
                    logging.info(sql)
                    db.execute(sql)



def exists_table(database_name: str, table_name: str):
    """
    检测表是否存在
    :param table_name: 数据库表名
    :return: 表是否存在，True 表示存在，False 表示不存在
    """
    # 构建 SQL 检测表是否存在语句
    with SQLiteWorkerContext(os.path.join(current_directory, f'{database_name}.db')) as db:
        sql = f'''
            SELECT name 
            FROM sqlite_master
            WHERE type = 'table'
            AND name  = '{table_name}'
        '''
        logging.info(sql)
        execute = db.execute(sql)
        return len(execute) > 0


def drop_table(database_name: str, table_name: str):
    """
    删除表
    :param table_name: 数据库表名
    """
    with SQLiteWorkerContext(os.path.join(current_directory, f'{database_name}.db')) as db:
        # 构建 SQL 删除表语句
        sql = f'''
            DROP TABLE IF EXISTS `{table_name}`
        '''
        logging.info(sql)
        db.execute(sql)


def truncate_table(database_name: str, table_name: str):
    """
    截断表
    :param table_name: 数据库表名
    """
    with SQLiteWorkerContext(os.path.join(current_directory, f'{database_name}.db')) as db:
        # 构建 SQL 截断表语句
        sql = f'''
            DELETE FROM  `{table_name}`
        '''
        logging.info(sql)
        db.execute(sql)


def insert(database_name: str, table_name: str, data: dict):
    """
    插入数据
    :param table_name 数据库表名
    :param data 数据
    """

    # 表是否存在
    exist = exists_table(database_name=database_name, table_name=table_name)
    if not exist:
        # 自动建表
        create_table(database_name=database_name, table_name=table_name, data=data)
    # 自动更新表
    update_table(database_name=database_name, table_name=table_name, data=data)
    with SQLiteWorkerContext(os.path.join(current_directory, f'{database_name}.db')) as db:
        # 从 data 字典中提取字段名和对应的值
        columns = ', '.join([f'`{k}`' for k in data.keys()])
        placeholders = ', '.join(['?'] * len(data))
        values = tuple(data.values())

        # 构建 SQL 插入语句
        sql = f'''
                INSERT INTO `{table_name}` ({columns})
                VALUES ({placeholders})
            '''
        logging.info(sql)
        db.execute(sql, values)


def insert_batch(database_name: str, table_name: str, data_list: list):
    """
    批量插入数据,批量插入数据的时候，list中的元素长度必须一致。
    :param table_name: 数据库表名
    :param data_list: 数据列表，每个元素为一个字典，表示一条记录
    """
    if not data_list:
        return  # 如果没有数据，直接返回
    # 表是否存在
    exist = exists_table(database_name=database_name, table_name=table_name)
    if not exist:
        # 自动建表
        create_table(database_name=database_name, table_name=table_name, data=data_list[0])
    # 自动更新表
    update_table(database_name=database_name, table_name=table_name, data=data_list[0])

    # 获取第一个字典的键作为字段名
    columns = list(data_list[0].keys())
    columns_str = ', '.join([f"`{c}`" for c in columns])

    # 构建插入语句的占位符
    placeholders = ', '.join(['?'] * len(columns))

    # 构建 SQL 插入语句
    sql = f'''
        INSERT INTO `{table_name}` ({columns_str})
        VALUES ({placeholders})
    '''

    # 提取所有记录的值
    values = [tuple(data.values()) for data in data_list]
    logging.info(sql)

    conn = sqlite3.connect(os.path.join(current_directory, f'{database_name}.db'))
    cursor = conn.cursor()
    # 开启事务
    conn.execute('BEGIN TRANSACTION')
    # 批量插入数据
    cursor.executemany(sql, values)
    # 提交事务
    conn.commit()
    conn.close()


def delete_by_ids(database_name: str, table_name: str, id_list: list):
    """
    批量删除
    :param table_name: 数据库表名
    :param id_list: id 列表，每个元素为一个 id
    """
    if not id_list:
        return  # 如果没有数据，直接返回

    # 构建 SQL 删除语句
    sql = f'''
        DELETE FROM `{table_name}`
        WHERE id IN ({', '.join(['?'] * len(id_list))})
    '''
    logging.info(sql)
    with SQLiteWorkerContext(os.path.join(current_directory, f'{database_name}.db')) as db:
        db.execute(sql, id_list)


def update_by_id(database_name: str, table_name: str, data: dict):
    """
    根据 id 更新数据
    :param table_name: 数据库表名
    :param data: 数据字典，键为字段名，值为要更新的数据
    """
    # 表是否存在
    exist = exists_table(database_name=database_name, table_name=table_name)
    if not exist:
        # 自动建表
        create_table(database_name=database_name, table_name=table_name, data=data)
    # 自动更新表
    update_table(database_name=database_name, table_name=table_name, data=data)

    # 构建 SET 子句
    set_clause = ', '.join([f"`{key}` = ?" for key in data.keys()])
    set_values = tuple(data.values())

    # 构建 SQL 更新语句
    sql = f'''
        UPDATE `{table_name}`
        SET {set_clause}
        WHERE id = ?
    '''

    # 合并 set_values 和 id
    values = set_values + (data['id'],)
    logging.info(sql)
    with SQLiteWorkerContext(os.path.join(current_directory, f'{database_name}.db')) as db:
        db.execute(sql, values)


def select_count(database_name: str, table_name: str, condition: list[dict] = None):
    """
    查询记录数
    :param table_name: 数据库表名
    :param condition: 条件字典，[{'field': 'command', 'value': 'ASBC', 'op': 'ct'}]
    :return: 记录数
    """
    if condition is None:
        condition = []
    # 表是否存在
    exist = exists_table(database_name=database_name, table_name=table_name)
    data = {}
    for c in condition:
        if 'value' in c:
            data[c['field']] = c['value']
        if 'value_0' in c:
            data[c['field']] = c['value_0']
        if 'value_1' in c:
            data[c['field']] = c['value_1']
    if not exist:
        # 自动建表
        create_table(database_name=database_name, table_name=table_name, data=data)
    # 自动更新表
    update_table(database_name=database_name, table_name=table_name, data=data)

    # 构建 WHERE 部分
    where_clauses = []
    if condition:
        for cond in condition:
            field = cond['field']
            op = cond['op']
            if op == 'ct':  # 模糊查询
                if str(cond['value']).strip() != '':
                    where_clauses.append(f"{field} LIKE '%{cond['value']}%'")
            elif op == 'eq':  # 精确查询
                if str(cond['value']).strip() != '':
                    if isinstance(cond['value'], str):
                        where_clauses.append(f"{field} = '{cond['value']}'")
                    else:
                        where_clauses.append(f"{field} = {cond['value']}")
            elif op == 'bt':  # 范围查询
                if str(cond['value_0']).strip() != '' and str(cond['value_1']).strip() != '':
                    if isinstance(cond['value_0'], str):
                        where_clauses.append(f"{field} BETWEEN '{cond['value_0']}' AND '{cond['value_1']}'")
                    else:
                        where_clauses.append(f"{field} BETWEEN {cond['value_0']} AND {cond['value_1']}")
            elif op == 'in' and 'values' in cond:  # 包含元素查询
                if isinstance(cond['values'], list) and len(cond['values']) > 0:
                    where_clauses.append(f"{field} in ({','.join(cond['values'])})")  # 这个可能有问题
            # 其他查询方式可以根据需要添加

    where_clause = " AND ".join(where_clauses)
    if where_clause:
        where_clause = f"WHERE {where_clause}"

    # 构建完整的 SQL 查询
    sql = f"SELECT count(*) FROM {table_name} {where_clause}"

    logging.info(sql)
    with SQLiteWorkerContext(os.path.join(current_directory, f'{database_name}.db')) as db:
        result = db.execute(sql)
        return result[0][0]


def select_page(database_name: str, table_name: str, condition: list[dict] = None, columns: list = None, page: int = 1,
                page_size: int = 10, order_by: list[dict] = None):
    """
    分页查询数据
    :param table_name: 数据库表名
    :param condition: 条件列表，field为字段名，value为条件值，op为查询方式【op为模糊，eq为精确查询，bt为范围查询（value_0,value_1）,in为包含查询（values:list）......】：[{'field':'command','value':'ASBC','op':'ct'}]
    :param columns: 要查询的列名列表，默认为所有列
    :param page: 当前页码，默认为1
    :param page_size: 每页记录数，默认为10
    :param order_by: 排序列表,field为字段名，value为排序值【'asc','desc'】：[{'field':'command','value':'asc'}]
    :return: 查询结果列表
    """
    # 表是否存在
    exist = exists_table(database_name=database_name, table_name=table_name)
    data = {}
    for c in condition:
        if 'value' in c:
            data[c['field']] = c['value']
        if 'value_0' in c:
            data[c['field']] = c['value_0']
        if 'value_1' in c:
            data[c['field']] = c['value_1']
    if not exist:
        # 自动建表
        create_table(database_name=database_name, table_name=table_name, data=data)
    # 自动更新表
    update_table(database_name=database_name, table_name=table_name, data=data)
    fields_ = get_table_fields(database_name, table_name)
    fields = [f[1] for f in fields_]
    # 构建 SELECT 部分
    if columns is None:
        select_columns = ", ".join(fields)
    else:
        select_columns = ", ".join(columns)

    # 构建 WHERE 部分
    where_clauses = []
    if condition:
        for cond in condition:
            field = cond['field']
            value = cond['value']
            op = cond['op']
            if op == 'ct':  # 模糊查询
                if value is not None and str(value).strip() != '':
                    where_clauses.append(f"{field} LIKE '%{value}%'")
            elif op == 'eq':  # 精确查询
                if value is not None and str(value).strip() != '':
                    if isinstance(value, str):
                        where_clauses.append(f"{field} = '{value}'")
                    else:
                        where_clauses.append(f"{field} = {value}")
            elif op == 'bt':  # 范围查询
                if cond['value_0'] is not None and str(cond['value_0']).strip() != '' and cond[
                    'value_1'] is not None and str(cond['value_1']).strip() != '':
                    if isinstance(cond['value_0'], str):
                        where_clauses.append(f"{field} BETWEEN '{cond['value_0']}' AND '{cond['value_1']}'")
                    else:
                        where_clauses.append(f"{field} BETWEEN {cond['value_0']} AND {cond['value_1']}")
            elif op == 'in' and 'values' in cond:  # 包含元素查询
                if cond['values'] is not None and isinstance(cond['values'], list) and len(cond['values']) > 0:
                    where_clauses.append(f"{field} in ({','.join(cond['values'])})")  # 这个可能有问题
            # 其他查询方式可以根据需要添加

    where_clause = " AND ".join(where_clauses)
    if where_clause:
        where_clause = f"WHERE {where_clause}"

    # 构建 ORDER BY 部分
    order_by_clauses = []
    if order_by:
        for order in order_by:
            field = order['field']
            value = order['value']
            order_by_clauses.append(f"{field} {value}")

    order_by_clause = ", ".join(order_by_clauses)
    if order_by_clause:
        order_by_clause = f"ORDER BY {order_by_clause}"

    # 构建 LIMIT 部分
    offset = (page - 1) * page_size
    if offset < 0:
        offset = 0
    limit_clause = f"LIMIT {offset}, {page_size}"

    # 构建完整的 SQL 查询
    sql = f"SELECT {select_columns} FROM {table_name} {where_clause} {order_by_clause} {limit_clause}"

    logging.info(sql)
    with SQLiteWorkerContext(os.path.join(current_directory, f'{database_name}.db')) as db:
        execute = db.execute(sql)
        result = []
        for res in execute:
            result.append(dict(zip(fields, res)))
        return result


def select_by_id(database_name: str, table_name: str, id: int):
    """
    根据 id 查询数据
    :param table_name: 数据库表名
    :param id: 要查询的记录的 id
    :return: 查询结果字典，如果没有找到则返回 None
    """
    # 表是否存在
    exist = exists_table(database_name=database_name, table_name=table_name)
    if not exist:
        # 自动建表
        create_table(database_name=database_name, table_name=table_name, data={})
    # 构建 SQL 查询语句
    sql = f'''
        SELECT *
        FROM `{table_name}`
        WHERE id = ?
    '''
    logging.info(sql)
    fields_ = get_table_fields(database_name, table_name)
    fields = [f[1] for f in fields_]
    with SQLiteWorkerContext(os.path.join(current_directory, f'{database_name}.db')) as db:
        execute = db.execute(sql, (id,))
        if len(execute) == 1:
            return dict(zip(fields, execute[0]))
        if len(execute) > 1:
            raise ValueError("数据库中存在多个相同id的数据")


def select_by_sql(database_name: str, sql: str):
    """
    根据原生SQL查询数据
    :param sql: 原生SQL查询语句
    :return: 查询结果列表
    """

    # 记录SQL语句和参数
    logging.info(f"Executing SQL: {sql}")
    with SQLiteWorkerContext(os.path.join(current_directory, f'{database_name}.db')) as db:
        execute = db.execute(sql)
        return execute


if __name__ == '__main__':
    # 配置日志记录
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # create_table('test_table', {'name': 'John', 'age': 30, 'is_active': True})
    # update_table('test_table', data={'name': 'John', 'age': 30, 'is_active': True, "address": "南昌"})
    # exists_table('test_table')
    # drop_table('test_table')
    # truncate_table('test_table')
    # insert(table_name='test_table', data={'name': 'John', 'age': 30, 'is_active': True, "address": "南昌"})
    # insert_batch(table_name='test_table',
    #              data_list=[
    #                  {'name': 'John', 'age': 30, 'is_active': True, "address": "南昌", "nickname": '小嘀咕'},
    #                  {'name': 'John', 'age': 31, 'is_active': True, "address": "北京"}
    #              ])
    # delete_by_ids(table_name='test_table', id_list=[1, 2])
    # update_by_id(table_name='test_table',
    #              data={'id': 3, 'name': 'John', 'age': 30, 'is_active': True, "address": "南昌", "nickname": '小嘀咕1'})
    # count = select_count(table_name='test_table',condition=[{"field": "name", "op": "ct", "value": "小嘀咕"}])
    # page = select_page(table_name='test_table', page=1, page_size=10,
    #                    condition=[{"field": "address", "op": "ct", "value": "南昌"}])
    # by_id = select_by_id(table_name='test_table', id=3)
