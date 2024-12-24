import logging
import os.path
import subprocess
import zipfile
import requests

from db.mysql import current_directory
from pathlib import Path

"""
数据库安装相关API
"""
port = 3366
mysql_name = "MySQL_PyOneDark"


def run_command(command, cwd, env=None):
    """
    执行命令
    :param command: 要执行的命令
    :param cwd: 工作目录
    :param env: 环境变量
    """
    logging.info(f"执行命令: {command}")
    logging.info(f"工作目录: {cwd}")
    logging.info(f"环境变量: {env}")
    if env is None:
        env = {**subprocess.os.environ}
    else:
        env = {**subprocess.os.environ, **env}
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logging.info(f"命令输出: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"命令执行失败: {e}")
        logging.error(f"错误输出: {e.stderr}")


def check_mysql_service_exists(name=mysql_name):
    if name is None:
        name = "mysql"
    try:
        subprocess.run(
            ["sc", "query", name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def mysql_download():
    """
    下载mysql-5.7.38-winx64
    下载地址：https://downloads.mysql.com/archives/get/p/23/file/mysql-5.7.38-winx64.zip
    1.检测本机是否存在文件夹
    2.下载压缩文件
    3.解压文件
    """
    try:
        url = 'https://downloads.mysql.com/archives/get/p/23/file/mysql-5.7.38-winx64.zip'
        # 如果不存在MYSQL免安装包，则去解压压缩包
        if not os.path.exists(os.path.join(current_directory, 'mysql-5.7.38-winx64')):
            # 如果不存在压缩包，则去下载压缩包
            if not os.path.exists(os.path.join(current_directory, 'mysql-5.7.38-winx64.zip')):
                logging.info("即将下载MYSQL压缩包")
                # 发送 GET 请求
                with requests.get(url=url, stream=True) as r:
                    # 确保请求成功
                    r.raise_for_status()

                    # 打开本地文件进行写入
                    with open(os.path.join(current_directory, os.path.basename(url)), 'wb') as f:
                        # 分块写入文件
                        for chunk in r.iter_content(chunk_size=8192):
                            logging.info("正在下载MYSQL压缩包...")
                            f.write(chunk)
                logging.info("下载MYSQL压缩包完成")
            else:
                logging.info("MYSQL压缩包已存在,解压即可")
            logging.info("即将解压MYSQL压缩包")
            # 打开 ZIP 文件
            with zipfile.ZipFile(os.path.join(current_directory, os.path.basename(url)), 'r') as zip_ref:
                # 解压所有文件到指定文件夹
                zip_ref.extractall(current_directory)
            logging.info("解压MYSQL压缩包完成")
        else:
            logging.info("MYSQL已存在,初始化即可")
    except:
        logging.info(
            "下载MYSQL失败，请去https://downloads.mysql.com/archives/get/p/23/file/mysql-5.7.38-winx64.zip手动下载，并将压缩文件放置到./db/mysql文件夹中")


def mysql_initialization():
    """
    数据库初始化
    【请以管理员身份执行】
    1.创建data文件夹
    2.创建my.ini配置文件
    3.执行安装命令 [mysqld -install]
    3.执行初始化命令 [mysqld --initialize-insecure]
    """
    try:
        base_dir = os.path.join(current_directory, 'mysql-5.7.38-winx64')
        data_dir = os.path.join(base_dir, 'data')
        ini_file = os.path.join(base_dir, 'my.ini')
        if os.path.exists(data_dir) is False:
            logging.info("创建MYSQL数据文件夹data")
            os.makedirs(data_dir)
        ini_data = f"""[client]
    port = {port}
    default-character-set = utf8
    
    [mysqld]
    # 设置为MYSQL的安装目录
    basedir = "{base_dir}"
    # 设置为MYSQL的数据目录
    datadir = "{data_dir}"
    
    port = {port}
    character_set_server = utf8
    sql_mode = NO_ENGINE_SUBSTITUTION,NO_AUTO_CREATE_USER
    
    #开启查询缓存
    explicit_defaults_for_timestamp = true"""
        with open(ini_file, 'w', encoding='utf-8') as f:
            logging.info("创建MYSQL配置文件my.ini")
            f.write(ini_data)
        # 执行安装命令
        command_install = ' '.join(['mysqld', '-install', mysql_name, f'--defaults-file="{ini_file}"'])
        logging.info(f"执行安装命令[{command_install}]")
        run_command(command=command_install, cwd=os.path.join(base_dir, 'bin'),
                    env={"MYSQL_HOME": os.path.join(base_dir, 'bin')})
        # 执行初始化命令
        # 如果数据文件夹已经有文件，则无法初始化，即不执行初始化
        folder = Path(data_dir)
        if not any(folder.iterdir()):
            command_init = ' '.join(['mysqld', '--initialize-insecure'])
            logging.info(f"执行初始化命令[{command_init}]")
            run_command(command=command_init, cwd=os.path.join(base_dir, 'bin'),
                        env={"MYSQL_HOME": os.path.join(base_dir, 'bin')})
    except:
        logging.info("数据库初始化失败，首次运行请以管理员权限运行程序")


def mysql_start_up():
    """
    启动mysql服务:[net start {mysql_name}]
    【请以管理员身份执行】
    """
    try:
        base_dir = os.path.join(current_directory, 'mysql-5.7.38-winx64')
        command_start_up = ' '.join(['net', 'start', mysql_name])
        logging.info(f"执行启动MYSQL命令[{command_start_up}]")
        run_command(command=command_start_up, cwd=os.path.join(base_dir, 'bin'),
                    env={"MYSQL_HOME": os.path.join(base_dir, 'bin')})
    except:
        logging.info("数据库初始化失败，首次运行请以管理员权限运行程序")


def mysql_stop():
    """
    停止mysql服务:[net stop {mysql_name}]
    【请以管理员身份执行】
    """
    base_dir = os.path.join(current_directory, 'mysql-5.7.38-winx64')
    command_stop = ' '.join(['net', 'stop', mysql_name])
    logging.info(f"执行停止MYSQL命令[{command_stop}]")
    run_command(command=command_stop, cwd=os.path.join(base_dir, 'bin'),
                env={"MYSQL_HOME": os.path.join(base_dir, 'bin')})


def mysql_uninstall():
    """
    卸载mysql服务:[sc delete {mysql_name}]
    【请以管理员身份执行】
    """
    base_dir = os.path.join(current_directory, 'mysql-5.7.38-winx64')
    command_uninstall = ' '.join(['sc', 'delete', mysql_name])
    logging.info(f"执行卸载MYSQL命令[{command_uninstall}]")
    run_command(command=command_uninstall, cwd=os.path.join(base_dir, 'bin'),
                env={"MYSQL_HOME": os.path.join(base_dir, 'bin')})


# 配置日志记录器
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
if __name__ == '__main__':
    # 下载压缩包并解压
    # mysql_download()
    # if not check_mysql_service_exists(mysql_name):
    #     mysql_initialization()
    #     mysql_start_up()
    # else:
    #     logging.info("MySQL 服务已存在，跳过安装步骤。")
    # mysql_stop()
    # mysql_uninstall()
    pass
