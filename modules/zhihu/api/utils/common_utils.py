import inspect
import os
import platform
import subprocess
import json
import logging
import threading

import psutil
import requests


def find_chrome_path():
    """
    获取chrome路径
    """
    system = platform.system()
    if system == 'Windows':
        # Windows
        import subprocess
        try:
            output = subprocess.check_output(['where', 'chrome']).decode('utf-8').strip()
            if output:
                return output
        except subprocess.CalledProcessError:
            pass

        # Try to find Chrome in common installation directories
        common_paths = [
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
    elif system == 'Darwin':
        # macOS
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        ]
        for path in paths:
            if os.path.exists(path):
                return path
    elif system == 'Linux':
        # Linux
        paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/google-chrome-beta",
            "/usr/bin/google-chrome-unstable"
        ]
        for path in paths:
            if os.path.exists(path):
                return path
    raise Exception("沒有找到Chrome路径。请手动填写")


def find_edge_path():
    """
    获取Microsoft Edge路径
    """
    system = platform.system()
    if system == 'Windows':
        # Windows
        try:
            output = subprocess.check_output(['where', 'msedge']).decode('utf-8').strip()
            if output:
                return output
        except subprocess.CalledProcessError:
            pass

        # Try to find Edge in common installation directories
        common_paths = [
            os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\Application\msedge.exe"),
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
    elif system == 'Darwin':
        # macOS
        paths = [
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            os.path.expanduser("~/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge")
        ]
        for path in paths:
            if os.path.exists(path):
                return path
    elif system == 'Linux':
        # Linux
        paths = [
            "/usr/bin/microsoft-edge",
            "/usr/bin/microsoft-edge-stable",
            "/usr/bin/microsoft-edge-beta",
            "/usr/bin/microsoft-edge-dev"
        ]
        for path in paths:
            if os.path.exists(path):
                return path
    raise Exception("沒有找到Microsoft Edge路径。请手动填写")


# 创建多级文件（不含文件）
def create_dir(file_path):
    if os.path.exists(file_path) is False:
        os.makedirs(file_path)


def kill_process_by_name(process_name: str = 'msedge.exe'):
    """
    关闭应用进程
    """
    if process_name == 'msedge':
        process_name = "msedge.exe"
    if process_name == 'chrome' or process_name == 'Chrome' or process_name == 'Chrome.exe':
        process_name = "chrome.exe"
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            try:
                process = psutil.Process(proc.info['pid'])
                process.terminate()
                logging.info(f"Terminated process: {proc.info['name']} (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                logging.error(f"Error terminating process: {e}")


# 创建锁对象
port_lock = threading.Lock()


async def kill_process_by_port(port):
    """
    关闭端口进程
    """
    logging.info(f"关闭端口进程，端口: {port}")
    with port_lock:
        try:
            connections = psutil.net_connections()
            for conn in connections:
                try:
                    if conn.laddr.port == port:
                        proc = psutil.Process(conn.pid)
                        logging.info(f"Killing process {proc.pid} using port {port}")
                        proc.terminate()  # 使用 terminate 而不是 kill
                        logging.info(f"Process {proc.pid} killed successfully.")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    logging.error(f"Error killing process: {e}")
                except Exception as e:
                    logging.error(f"Error killing process: {e}")
        except Exception as e:
            logging.error(f"Error closing port: {e}")


async def kill_processes_by_user_data_dir(user_data_dir):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'chrome.exe':
                cmdline = proc.info['cmdline']
                if cmdline and f'--user-data-dir={user_data_dir}' in cmdline:
                    os.kill(proc.info['pid'], 9)
                    print(f"Killed process {proc.info['pid']} with user-data-dir {user_data_dir}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            logging.error(f"Error closing user_data_dir:{user_data_dir}")


async def close_browser_by_domain(domain):
    # 关闭页面
    try:
        if hasattr(domain, "content"):
            if hasattr(domain.content, "pages"):
                pages = domain.content.pages
                for page in pages:
                    # 获取对象的方法
                    close = getattr(page, "close")
                    # 检查方法是否是协程函数
                    if inspect.iscoroutinefunction(close):
                        # 如果是协程函数，使用 await 调用
                        return await close()
                    else:
                        # 如果不是协程函数，直接调用
                        return close()
    except Exception as e:
        logging.error(f"Error closing page: {e}")
    try:
        if hasattr(domain, "page"):
            # 获取对象的方法
            close = getattr(domain.page, "close")
            # 检查方法是否是协程函数
            if inspect.iscoroutinefunction(close):
                # 如果是协程函数，使用 await 调用
                return await close()
            else:
                # 如果不是协程函数，直接调用
                return close()
    except Exception as e:
        logging.error(f"Error closing page: {e}")
    try:
        if hasattr(domain, "content"):
            # 获取对象的方法
            close = getattr(domain.content, "close")
            # 检查方法是否是协程函数
            if inspect.iscoroutinefunction(close):
                # 如果是协程函数，使用 await 调用
                return await close()
            else:
                # 如果不是协程函数，直接调用
                return close()
    except Exception as e:
        logging.error(f"Error closing page: {e}")
    try:
        if hasattr(domain, "browser"):
            # 获取对象的方法
            close = getattr(domain.browser, "close")
            # 检查方法是否是协程函数
            if inspect.iscoroutinefunction(close):
                # 如果是协程函数，使用 await 调用
                return await close()
            else:
                # 如果不是协程函数，直接调用
                return close()
    except Exception as e:
        logging.error(f"Error closing page: {e}")
    try:
        if hasattr(domain, "close"):
            # 获取对象的方法
            close = getattr(domain.chrome_process, "close")
            # 检查方法是否是协程函数
            if inspect.iscoroutinefunction(close):
                # 如果是协程函数，使用 await 调用
                return await close()
            else:
                # 如果不是协程函数，直接调用
                return close()
    except Exception as e:
        logging.error(f"Error closing chrome_process: {e}")


def upload_pic_go(picDir: str) -> str:
    """
    图片上传到图床（前提是将本地PicGo打开并开启Server服务）
    :param picDir: 本地图片全路径
    :return:返回网络图片链接
    """
    # 定义URL
    url = 'http://127.0.0.1:36677/upload'

    data = {'list': [picDir]}

    response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
    loads = json.loads(response.content.decode('utf-8'))
    return loads['result'][0]


def ping_website(url):
    # 检查网站通不通，例如：ping_website("www.zhihu.com")
    try:
        # 去掉协议前缀
        if url.startswith("http://") or url.startswith("https://"):
            url = url.split("//")[1]

        # 根据操作系统选择合适的 ping 命令参数
        if platform.system().lower() == "windows":
            ping_cmd = ["ping", "-n", "1", url]
        else:
            ping_cmd = ["ping", "-c", "1", url]

        # 使用 ping 命令检查网站是否可以访问
        result = subprocess.run(ping_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            logging.info(f"网站 {url} 可以访问")
            return True
        else:
            logging.error(f"网站 {url} 无法访问")
            return False
    except Exception as e:
        logging.error(f"发生错误: {e}")
        return False
