import asyncio
import datetime
import json

import aiomysql
import logging

import nest_asyncio
from pymysql import OperationalError

from gui.utils.loop_util import is_event_loop_running
from concurrent.futures import ThreadPoolExecutor

"""
数据库操作相关API
"""
# 定义类型映射

type_mapping = {
    int: 'INT',
    float: 'FLOAT',
    # str: 'VARCHAR(255)',
    str: 'TEXT',
    bool: 'BOOLEAN',
    datetime.datetime: 'DATETIME',
    datetime.date: 'DATE',
    None: 'TEXT',
}
# 创建一个线程池
executor = ThreadPoolExecutor()


async def create_pool_with_no_db(host='localhost', port=3366, user='root', password=None, autocommit=True, minsize=1,
                                 maxsize=100):
    """
    创建数据库连接池（不带数据库）
    """
    pool = await aiomysql.create_pool(
        host=host,
        port=port,
        user=user,
        password=password,
        autocommit=autocommit,  # 自动提交事务
        minsize=minsize,  # 连接池最小连接数
        maxsize=maxsize  # 连接池最大连接数
    )
    return pool


async def create_pool(db, host='localhost', port=3366, user='root', password=None,
                      autocommit=True, minsize=1, maxsize=100):
    """
    创建数据库连接池
    """
    try:
        pool = await aiomysql.create_pool(
            host=host,
            port=port,
            user=user,
            password=password,
            db=db,
            autocommit=autocommit,  # 自动提交事务
            minsize=minsize,  # 连接池最小连接数
            maxsize=maxsize  # 连接池最大连接数
        )
        return pool
    except OperationalError as e:
        if e.args[0] == 1049:
            logging.error(f"数据库不存在：【{db}】，自动创建数据库：【{db}】")
            pool_ = await create_pool_with_no_db(host=host, port=port, user=user, password=password,
                                                 autocommit=True, minsize=1, maxsize=10)
            try:
                await create_database(pool_, db)
                pool = await aiomysql.create_pool(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    db=db,
                    autocommit=autocommit,  # 自动提交事务
                    minsize=minsize,  # 连接池最小连接数
                    maxsize=maxsize  # 连接池最大连接数
                )
                return pool
            finally:
                await close_pool(pool_)
        else:
            raise OperationalError


async def close_pool(pool):
    """
    关闭连接池
    :param pool: 数据库连接池
    """
    if pool:
        pool.close()
        await pool.wait_closed()


async def create_database(pool, database_name: str, character='utf8', collate='utf8_general_ci'):
    """
    创建数据库
    :param pool: 数据库连接池
    :param database_name: 数据库名称
    :return:
    """
    # 构建 SQL 检测表是否存在语句
    # 创建数据库的 SQL 语句，指定字符集为 utf8，排序规则为 utf8_general_ci
    create_database_query = f"CREATE DATABASE {database_name} CHARACTER SET {character} COLLATE {collate}"
    logging.info(create_database_query)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 执行 SQL 检测表是否存在语句
            await cur.execute(create_database_query)
    logging.info(f"创建数据库完毕：【{database_name}】")


async def drop_database(pool, database_name: str):
    """
    删除数据库
    :param pool: 数据库连接池
    :param database_name: 数据库名称
    :return:
    """
    # 构建 SQL 检测表是否存在语句
    # 创建数据库的 SQL 语句，指定字符集为 utf8，排序规则为 utf8_general_ci
    # 删除数据库的 SQL 语句
    drop_database_query = f"DROP DATABASE IF EXISTS {database_name}"
    logging.info(drop_database_query)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 执行 SQL 检测表是否存在语句
            await cur.execute(drop_database_query)
    logging.info(f"删除数据库完毕：【{database_name}】")


async def check_database(pool, database_name: str):
    """
    检测数据库是否存在
    :param pool: 数据库连接池
    :param database_name: 数据库名称
    :return:
    """
    # 构建 SQL 检测表是否存在语句
    # 创建数据库的 SQL 语句，指定字符集为 utf8，排序规则为 utf8_general_ci
    # 删除数据库的 SQL 语句
    check_database_query = f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{database_name}'"
    logging.info(check_database_query)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 执行 SQL 检测表是否存在语句
            await cur.execute(check_database_query)
            # 获取查询结果
            result = await cur.fetchone()
            if result:
                logging.info(f"数据库【{database_name}】存在")
            else:
                logging.info(f"数据库【{database_name}】不存在")
            return result  # 返回表是否存在


async def exists_table(pool, table_name: str):
    """
    检测表是否存在
    :param pool: 数据库连接池
    :param table_name: 数据库表名
    :return: 表是否存在，True 表示存在，False 表示不存在
    """
    # 构建 SQL 检测表是否存在语句
    sql = f'''
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
        AND table_name = %s
    '''
    logging.info(sql % (table_name,))
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 执行 SQL 检测表是否存在语句
            await cur.execute(sql, (table_name,))
            # 获取查询结果
            result = await cur.fetchone()
            return result[0] > 0  # 返回表是否存在


async def create_table(pool, table_name: str, data: dict):
    """
    创建表
    :param pool: 数据库连接池
    :param table_name: 数据库表名
    :param data: 数据字典，键为字段名，值为字段类型
    """

    # 自动添加主键 id
    columns = ['id INT AUTO_INCREMENT PRIMARY KEY']

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
    columns.append('updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')

    # 构建 SQL 创建表语句
    sql = f'''
            CREATE TABLE `{table_name}` (
                {', '.join(columns)}
            )
        '''
    logging.info(sql)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 执行 SQL 创建表语句
            await cur.execute(sql)


async def drop_table(pool, table_name: str):
    """
    删除表
    :param pool: 数据库连接池
    :param table_name: 数据库表名
    """
    # 构建 SQL 删除表语句
    sql = f'''
        DROP TABLE IF EXISTS `{table_name}`
    '''
    logging.info(sql)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 执行 SQL 删除表语句
            await cur.execute(sql)


async def truncate_table(pool, table_name: str):
    """
    截断表
    :param pool: 数据库连接池
    :param table_name: 数据库表名
    """
    # 构建 SQL 截断表语句
    sql = f'''
        TRUNCATE TABLE `{table_name}`
    '''
    logging.info(sql)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 执行 SQL 截断表语句
            await cur.execute(sql)


async def update_table(pool, table_name: str, data: dict):
    """
    更新表结构
    :param pool: 数据库连接池
    :param table_name: 数据库表名
    :param data: 数据字典，键为字段名，值为字段类型
    """
    # 保留的字段
    reserved_fields = {'id', 'created_at', 'updated_at'}
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 获取当前表的字段信息
            await cur.execute(f"DESCRIBE `{table_name}`")
            current_fields = await cur.fetchall()
            current_fields_dict = {field[0]: field[1] for field in current_fields}

            # 构建 ALTER TABLE 语句
            alter_statements = []
            if data:
                for key, value in data.items():
                    field_type = type_mapping.get(type(value))
                    if field_type is None:
                        field_type = 'TEXT'
                    if key not in current_fields_dict and key not in reserved_fields:
                        alter_statements.append(f"ADD COLUMN `{key}` {field_type}")
                    elif key in current_fields_dict and current_fields_dict[
                        key] != field_type and key not in reserved_fields:
                        alter_statements.append(f"MODIFY COLUMN `{key}` {field_type}")

            if alter_statements:
                # 构建 SQL 更新表语句
                sql = f'''
                    ALTER TABLE `{table_name}`
                    {', '.join(alter_statements)}
                '''
                # 执行 SQL 更新表语句
                logging.info(sql)
                await cur.execute(sql)


async def insert(pool, table_name: str, data: dict):
    """
    插入数据
    :param pool 数据库连接池
    :param table_name 数据库表名
    :param data 数据
    """
    # 表是否存在
    exist = await exists_table(pool=pool, table_name=table_name)
    if not exist:
        # 自动建表
        await create_table(pool=pool, table_name=table_name, data=data)
    # 自动更新表
    await update_table(pool=pool, table_name=table_name, data=data)

    # # data数据合法性检测
    # for key, value in data.items():
    #     if value is None:
    #         data[key] = str('NULL')
    #     if not isinstance(value, (str, int, float, bool, datetime.date, datetime.datetime)):
    #         # 强行转为字符串
    #         data[key] = str(value)
    #     if isinstance(value, datetime.date):
    #         data[key] = value.strftime('%Y-%m-%d')
    #     if isinstance(value, datetime.datetime):
    #         data[key] = value.strftime('%Y-%m-%d %H:%M:%S')

    # 从 data 字典中提取字段名和对应的值
    columns = ', '.join([f'`{k}`' for k in data.keys()])
    placeholders = ', '.join(['%s'] * len(data))
    values = tuple(data.values())

    # 构建 SQL 插入语句
    sql = f'''
            INSERT INTO `{table_name}` ({columns})
            VALUES ({placeholders})
        '''
    logging.info(sql % values)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 执行 SQL 插入语句
            await cur.execute(sql, values)


async def insert_batch(pool, table_name: str, data_list: list):
    """
    批量插入数据
    :param pool: 数据库连接池
    :param table_name: 数据库表名
    :param data_list: 数据列表，每个元素为一个字典，表示一条记录
    """
    if not data_list:
        return  # 如果没有数据，直接返回
    # 表是否存在
    exist = await exists_table(pool=pool, table_name=table_name)
    if not exist:
        # 自动建表
        await create_table(pool=pool, table_name=table_name, data=data_list[0])
    # 自动更新表
    await update_table(pool=pool, table_name=table_name, data=data_list[0])

    # for data in data_list:
    #     # data数据合法性检测
    #     for key, value in data.items():
    #         if value is None:
    #             data[key] = str('NULL')
    #         if not isinstance(value, (str, int, float, bool, datetime.date, datetime.datetime)):
    #             # 强行转为字符串
    #             data[key] = str(value)
    #         if isinstance(value, datetime.date):
    #             data[key] = value.strftime('%Y-%m-%d')
    #         if isinstance(value, datetime.datetime):
    #             data[key] = value.strftime('%Y-%m-%d %H:%M:%S')

    # 获取第一个字典的键作为字段名
    columns = list(data_list[0].keys())
    columns_str = ', '.join([f"`{c}`" for c in columns])

    # 构建插入语句的占位符
    placeholders = ', '.join(['%s'] * len(columns))

    # 构建 SQL 插入语句
    sql = f'''
        INSERT INTO `{table_name}` ({columns_str})
        VALUES ({placeholders})
    '''

    # 提取所有记录的值
    values = [tuple(data.values()) for data in data_list]
    logging.info(sql)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 执行批量插入
            await cur.executemany(sql, values)


async def delete(pool, table_name: str, condition: dict):
    """
    条件删除
    :param pool: 数据库连接池
    :param table_name: 数据库表名
    :param condition: 条件字典，键为字段名，值为条件值
    """
    # 构建 WHERE 子句
    where_clause = ' AND '.join([f"`{key}` = %s" for key in condition.keys()])
    where_values = tuple(condition.values())

    # 构建 SQL 删除语句
    sql = f'''
        DELETE FROM `{table_name}`
        WHERE {where_clause}
    '''
    logging.info(sql % (where_values))
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 执行 SQL 删除语句
            await cur.execute(sql, where_values)


async def delete_by_ids(pool, table_name: str, id_list: list):
    """
    批量删除
    :param pool: 数据库连接池
    :param table_name: 数据库表名
    :param id_list: id 列表，每个元素为一个 id
    """
    if not id_list:
        return  # 如果没有数据，直接返回

    # 构建 SQL 删除语句
    sql = f'''
        DELETE FROM `{table_name}`
        WHERE id IN ({', '.join(['%s'] * len(id_list))})
    '''
    logging.info(sql)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 执行批量删除
            await cur.execute(sql, id_list)


async def update(pool, table_name: str, data: dict, condition: dict):
    """
    更新数据
    :param pool: 数据库连接池
    :param table_name: 数据库表名
    :param data: 数据字典，键为字段名，值为要更新的数据
    :param condition: 条件字典，键为字段名，值为条件值
    """
    # 表是否存在
    exist = await exists_table(pool=pool, table_name=table_name)
    if not exist:
        # 自动建表
        await create_table(pool=pool, table_name=table_name, data=data)
    # 自动更新表
    await update_table(pool=pool, table_name=table_name, data=data)

    # 构建 SET 子句
    set_clause = ', '.join([f"`{key}` = %s" for key in data.keys()])
    set_values = tuple(data.values())

    # 构建 WHERE 子句
    where_clause = ' AND '.join([f"`{key}` = %s" for key in condition.keys()])
    where_values = tuple(condition.values())

    # 构建 SQL 更新语句
    sql = f'''
        UPDATE `{table_name}`
        SET {set_clause}
        WHERE {where_clause}
    '''

    # 合并 set_values 和 where_values
    values = set_values + where_values
    logging.info(sql % values)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 执行 SQL 更新语句
            await cur.execute(sql, values)


async def update_by_id(pool, table_name: str, data: dict):
    """
    根据 id 更新数据
    :param pool: 数据库连接池
    :param table_name: 数据库表名
    :param data: 数据字典，键为字段名，值为要更新的数据
    """
    # 表是否存在
    exist = await exists_table(pool=pool, table_name=table_name)
    if not exist:
        # 自动建表
        await create_table(pool=pool, table_name=table_name, data=data)
    # 自动更新表
    await update_table(pool=pool, table_name=table_name, data=data)
    # # data数据合法性检测
    # for key, value in data.items():
    #     if value is None:
    #         data[key] = str('NULL')
    #     if not isinstance(value, (str, int, float, bool, datetime.date, datetime.datetime)):
    #         # 强行转为字符串
    #         data[key] = str(value)
    #     if isinstance(value, datetime.date):
    #         data[key] = value.strftime('%Y-%m-%d')
    #     if isinstance(value, datetime.datetime):
    #         data[key] = value.strftime('%Y-%m-%d %H:%M:%S')
    # 构建 SET 子句
    set_clause = ', '.join([f"`{key}` = %s" for key in data.keys()])
    set_values = tuple(data.values())

    # 构建 SQL 更新语句
    sql = f'''
        UPDATE `{table_name}`
        SET {set_clause}
        WHERE id = %s
    '''

    # 合并 set_values 和 id
    values = set_values + (data['id'],)
    logging.info(sql % values)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 执行 SQL 更新语句
            await cur.execute(sql, values)


async def update_batch(pool, table_name: str, data_list: list):
    """
    批量更新数据
    :param pool: 数据库连接池
    :param table_name: 数据库表名
    :param data_list: 数据列表，每个元素为一个字典，表示一条记录，必须包含 'id' 字段
    """
    if not data_list:
        return  # 如果没有数据，直接返回

    # 表是否存在
    exist = await exists_table(pool=pool, table_name=table_name)
    if not exist:
        # 自动建表
        await create_table(pool=pool, table_name=table_name, data=data_list[0])
    # 自动更新表
    await update_table(pool=pool, table_name=table_name, data=data_list[0])

    # for data in data_list:
    #     # data数据合法性检测
    #     for key, value in data.items():
    #         if value is None:
    #             data[key] = str('NULL')
    #         if not isinstance(value, (str, int, float, bool, datetime.date, datetime.datetime)):
    #             # 强行转为字符串
    #             data[key] = str(value)
    #         if isinstance(value, datetime.date):
    #             data[key] = value.strftime('%Y-%m-%d')
    #         if isinstance(value, datetime.datetime):
    #             data[key] = value.strftime('%Y-%m-%d %H:%M:%S')
    # 获取第一个字典的键作为字段名（排除 'id'）
    columns = list(data_list[0].keys())
    columns.remove('id')

    # 构建更新语句的 SET 子句
    set_clause = ', '.join([f"`{column}` = %s" for column in columns])

    # 构建 SQL 更新语句
    sql = f'''
        UPDATE `{table_name}`
        SET {set_clause}
        WHERE id = %s
    '''

    # 提取所有记录的值
    values = []
    for data in data_list:
        # 提取字段值（排除 'id'）
        field_values = [data[column] for column in columns]
        # 添加 'id' 值
        field_values.append(data['id'])
        # 将值列表转换为元组
        values.append(tuple(field_values))
    logging.info(sql)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 执行批量更新
            await cur.executemany(sql, values)


async def select_list(pool, table_name: str, condition: list[dict] = None, columns: list = None, order_by: list = None,
                      order_direction: list = None):
    """
    查询数据
    :param pool: 数据库连接池
    :param table_name: 数据库表名
    :param condition: 条件列表，field为字段名，value为条件值，op为查询方式【op为模糊，eq为精确查询，bt为范围查询（value_0,value_1）,in为包含查询（values:list）......】：[{'field':'command','value':'ASBC','op':'ct'}]
    :param columns: 要查询的列名列表，默认为所有列
    :return: 查询结果列表
    """
    # 表是否存在
    exist = await exists_table(pool=pool, table_name=table_name)
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
        await create_table(pool=pool, table_name=table_name, data=data)
    # 自动更新表
    await asyncio.shield(update_table(pool=pool, table_name=table_name, data=data))

    # 构建 SELECT 部分
    if columns is None:
        select_columns = "*"
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

    # 构建完整的 SQL 查询
    sql = f"SELECT {select_columns} FROM {table_name} {where_clause} {order_by_clause}"

    logging.info(sql)
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # 执行 SQL 查询语句
            await cur.execute(sql)
            # 获取查询结果
            result = await cur.fetchall()
            return result


async def select_last_one(pool, table_name: str, condition: list[dict] = None):
    """
    查询最新一条数据
    :param pool: 数据库连接池
    :param table_name: 数据库表名
    :param condition: 条件列表，field为字段名，value为条件值，op为查询方式【op为模糊，eq为精确查询，bt为范围查询（value_0,value_1）,in为包含查询（values:list）......】：[{'field':'command','value':'ASBC','op':'ct'}]
    :return: 查询结果列表
    """
    # 表是否存在
    exist = await exists_table(pool=pool, table_name=table_name)
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
        await create_table(pool=pool, table_name=table_name, data=data)
    # 自动更新表
    await asyncio.shield(update_table(pool=pool, table_name=table_name, data=data))

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

    # 构建完整的 SQL 查询
    sql = f"SELECT * FROM {table_name} {where_clause} limit 0,1"

    logging.info(sql)
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # 执行 SQL 查询语句
            await cur.execute(sql)
            # 获取查询结果
            result = await cur.fetchall()
            return result


async def select_page(pool, table_name: str, condition: list[dict] = None, columns: list = None, page: int = 1,
                      page_size: int = 10, order_by: list[dict] = None):
    """
    分页查询数据
    :param pool: 数据库连接池
    :param table_name: 数据库表名
    :param condition: 条件列表，field为字段名，value为条件值，op为查询方式【op为模糊，eq为精确查询，bt为范围查询（value_0,value_1）,in为包含查询（values:list）......】：[{'field':'command','value':'ASBC','op':'ct'}]
    :param columns: 要查询的列名列表，默认为所有列
    :param page: 当前页码，默认为1
    :param page_size: 每页记录数，默认为10
    :param order_by: 排序列表,field为字段名，value为排序值【'asc','desc'】：[{'field':'command','value':'asc'}]
    :return: 查询结果列表
    """
    # 表是否存在
    exist = await exists_table(pool=pool, table_name=table_name)
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
        await create_table(pool=pool, table_name=table_name, data=data)
    # 自动更新表
    await asyncio.shield(update_table(pool=pool, table_name=table_name, data=data))

    # 构建 SELECT 部分
    if columns is None:
        select_columns = "*"
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
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # 执行 SQL 查询语句
            await cur.execute(sql)
            # 获取查询结果
            result = await cur.fetchall()
            return result


async def select_by_id(pool, table_name: str, id: int):
    """
    根据 id 查询数据
    :param pool: 数据库连接池
    :param table_name: 数据库表名
    :param id: 要查询的记录的 id
    :return: 查询结果字典，如果没有找到则返回 None
    """
    # 表是否存在
    exist = await exists_table(pool=pool, table_name=table_name)
    if not exist:
        # 自动建表
        await create_table(pool=pool, table_name=table_name, data={})
    # 构建 SQL 查询语句
    sql = f'''
        SELECT *
        FROM `{table_name}`
        WHERE id = %s
    '''
    logging.info(sql % id)
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # 执行 SQL 查询语句
            await cur.execute(sql, (id,))
            # 获取查询结果
            result = await cur.fetchone()
            return result


async def select_count(pool, table_name: str, condition: list[dict] = None):
    """
    查询记录数
    :param pool: 数据库连接池
    :param table_name: 数据库表名
    :param condition: 条件字典，[{'field': 'command', 'value': 'ASBC', 'op': 'ct'}]
    :return: 记录数
    """
    # 表是否存在
    exist = await exists_table(pool=pool, table_name=table_name)
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
        await create_table(pool=pool, table_name=table_name, data=data)
    # 自动更新表
    await asyncio.shield(update_table(pool=pool, table_name=table_name, data=data))

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
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 执行 SQL 查询记录数语句
            await cur.execute(sql)
            # 获取查询结果
            result = await cur.fetchone()
            return result[0]  # 返回记录数


async def select_by_sql(pool, sql: str):
    """
    根据原生SQL查询数据
    :param pool: 数据库连接池
    :param sql: 原生SQL查询语句
    :param params: SQL查询参数，用于替换SQL中的占位符
    :return: 查询结果列表
    """

    # 记录SQL语句和参数
    logging.info(f"Executing SQL: {sql}")

    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # 执行 SQL 查询语句
            await cur.execute(sql)
            # 获取查询结果
            result = await cur.fetchall()
            return result if result else None


def select_by_sql_by_database_table(database_name, sql: str):
    """
    :param database_name: 数据库名称
    :param sql: SQL
    """

    async def async_slot_function():
        pool = await create_pool(db=database_name)
        try:
            page_data = await select_by_sql(pool=pool, sql=sql)
            return page_data
        except:
            traceback.print_exc()
            exc_info = traceback.format_exc()
        finally:
            await close_pool(pool)

    data = None
    if is_event_loop_running():
        loop = asyncio.get_event_loop()
        # 使用线程池执行异步任务
        future = executor.submit(lambda: asyncio.run(async_slot_function()))
        try:
            data = future.result(timeout=10)  # 阻塞等待结果
        except Exception as e:
            import traceback
            traceback.print_exc()
            exc_info = traceback.format_exc()
    else:
        # 获取或创建新的事件循环
        data = asyncio.run(async_slot_function())

    # 获取异步槽函数的结果
    return data


def select_list_by_database_table(database_name, table_name, conditions: list[dict] = None,
                                  orderby_list=None) -> list[
    dict]:
    """
    :param conditions: 条件列表，格式：[{field:field,value:value,op:op},,,,]。field为字段名，value为条件值，op为查询方式【op为模糊，eq为精确查询，bt为范围查询（value_0,value_1）,in为包含查询（values:list）......】：[{'field':'command','value':'ASBC','op':'ct'}]
    :param orderby_list: 排序列表,field为字段名，value为排序值【'asc','desc'】：[{'field':'command','value':'asc'}]
    """
    if orderby_list is None:
        orderby_list = []

    async def async_slot_function():
        pool = await create_pool(db=database_name)
        try:
            page_data = await select_list(pool=pool, table_name=table_name,
                                          condition=conditions, columns=None,
                                          order_by=[{'field': odb[0], 'value': odb[1]} for odb in orderby_list])
            return page_data
        except:
            traceback.print_exc()
            exc_info = traceback.format_exc()
        finally:
            await close_pool(pool)

    data_list = None
    if is_event_loop_running():
        loop = asyncio.get_event_loop()
        # 使用线程池执行异步任务
        future = executor.submit(lambda: asyncio.run(async_slot_function()))
        try:
            data_list = future.result(timeout=10)  # 阻塞等待结果
        except Exception as e:
            import traceback
            traceback.print_exc()
            exc_info = traceback.format_exc()
    else:
        # 获取或创建新的事件循环
        data_list = asyncio.run(async_slot_function())

    # 获取异步槽函数的结果
    # 这里要对data_list进行逆向序列化
    if data_list is not None:
        for data in data_list:
            for k, v in data.items():
                if k.endswith('_list'):
                    try:
                        # 尝试逆向序列化
                        data[k] = json.loads(v)
                    except:
                        pass

    return data_list


def select_by_id_by_database_table(database_name, table_name, id: int):
    """
    :param database_name: 数据库名称
    :param table_name: 表名称
    :param id: ID
    """

    async def async_slot_function():
        pool = await create_pool(db=database_name)
        try:
            page_data = await select_by_id(pool=pool, table_name=table_name, id=id)
            return page_data
        except:
            traceback.print_exc()
            exc_info = traceback.format_exc()
        finally:
            await close_pool(pool)

    data = None
    if is_event_loop_running():
        loop = asyncio.get_event_loop()
        # 使用线程池执行异步任务
        future = executor.submit(lambda: asyncio.run(async_slot_function()))
        try:
            data = future.result(timeout=10)  # 阻塞等待结果
        except Exception as e:
            import traceback
            traceback.print_exc()
            exc_info = traceback.format_exc()
    else:
        # 获取或创建新的事件循环
        data = asyncio.run(async_slot_function())

    # 获取异步槽函数的结果
    # 这里要对data_list进行逆向序列化
    if data is not None:
        for k, v in data.items():
            if k.endswith('_list'):
                try:
                    # 尝试逆向序列化
                    data[k] = json.loads(v)
                except:
                    pass

    return data


async def main():
    init_data = {
        'username': "张三丰",
        'password': "太极",
        'email': "zhangsan@example.com",
        'age': 30,
        'status': True,
        'birthday': datetime.date.today(),
        'address': "武当山",
        'start': 0,
        'select': 0,
        'order': "真假"
    }

    pool = await create_pool_with_no_db()

    try:
        # 插入数据
        # await insert(pool=pool, table_name='user', data=init_data)
        # # 批量插入
        # await insert_batch(pool=pool, table_name='user', data_list=[init_data])
        #
        # # 查询列表
        # data_list: list[dict] = await select_list(pool=pool, table_name='user', condition=None, order_by=['id'],
        #                                           order_direction=['DESC'])
        # # ID查询
        # data: dict = await select_by_id(pool=pool, table_name='user', id=1)
        #
        # # 并发更新数据
        # await asyncio.gather(
        #     *[update(pool=pool, table_name='user', data=data, condition={"id": data['id']}) for data in data_list])
        #
        # # 批量更新
        # await update_batch(pool=pool, table_name='user', data_list=data_list)
        #
        # # 查询数量
        # count = await select_count(pool=pool, table_name='user', condition=[
        #     {'field': 'status', 'value': True, 'op': 'eq'},
        #     {'field': 'age', 'value': 30, 'op': 'eq'},
        #     {'field': 'birthday', 'value': datetime.date.today(), 'op': 'eq'},
        #     {'field': 'address', 'value': "武当山", 'op': 'eq'},
        #     {'field': 'start', 'value': 0, 'op': 'eq'},
        #     {'field': 'select', 'value': 0, 'op': 'eq'},
        #     {'field': 'order', 'value': "真", 'op': 'eq'}
        # ])
        #
        # # 分页查询
        # page_data = await select_page(pool=pool, table_name='user',
        #                               condition=[{'field': 'command', 'value': 'ASBC', 'op': 'ct'}], columns=None,
        #                               page=1, page_size=10, order_by=[{'field': 'age', 'value': 'asc'}])
        #
        # # 并发删除数据
        # await asyncio.gather(
        #     *[delete(pool=pool, table_name='user', condition={"id": data['id']}) for data in data_list])
        #
        # # 批量删除
        # await delete_by_ids(pool=pool, table_name='user', id_list=[data['id'] for data in data_list])
        await check_database(pool, 'mysql')
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    # 配置日志记录
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    nest_asyncio.apply()
    asyncio.run(main())
