# 数据库模块
import logging
import os

from db.mysql.mysql_install import check_mysql_service_exists, mysql_initialization, mysql_start_up, mysql_download

# mysql服务初始化检测
if not check_mysql_service_exists():
    logging.info("MySQL 服务不存在，开始安装。")
    mysql_download()
    mysql_initialization()
    mysql_start_up()
else:
    logging.info("MySQL 服务已存在，跳过安装步骤。")

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件所在的目录
current_directory = os.path.dirname(current_file_path)
# 获取当前文件所在目录的父级目录
parent_directory = os.path.dirname(current_directory)
# 获取当前文件所在目录的爷爷级别目录
grandparent_directory = os.path.dirname(parent_directory)
# 获取当前文件所在目录的曾祖父级别目录
great_grandparent_directory = os.path.dirname(grandparent_directory)
# 路径拼接
# os.path.join(current_directory, "xxx")
