import asyncio
import os
import atexit

import ctypes
import signal
import subprocess
import sys
import time

import psutil
import qasync
from PySide6.QtWidgets import QWidget, QApplication

from framework.utils import current_directory
from framework.widgets.framework_widgets.c_splash_screen.c_splash_screen import CSplashScreen

"""
APP锁，防止打开多个实例。
"""


def get_all_window_mapping():
    """
    获取所有窗口句柄
    :return:
    """
    handles_mapping = {}
    import ctypes
    # 定义回调函数
    def foreach_window(hwnd, lParam):
        if ctypes.windll.user32.IsWindowVisible(hwnd):
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd) + 1
            buffer = ctypes.create_unicode_buffer(length)
            ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length)
            title = buffer.value if buffer.value else "No Title"
            # print(f"显式Window handle: {hwnd}, Title: {title}")
            handles_mapping[title] = hwnd
        return True

    # 定义 EnumWindows 的回调函数类型
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))

    # 调用 EnumWindows
    ctypes.windll.user32.EnumWindows(EnumWindowsProc(foreach_window), 0)

    # 获取所有窗口句柄
    def get_all_window_handles():
        def callback(hwnd, lParam):
            hwnds = ctypes.cast(lParam, ctypes.POINTER(ctypes.py_object)).contents.value
            hwnds.append(hwnd)
            return True

        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int),
                                             ctypes.POINTER(ctypes.py_object))
        hwnds = []
        lParam = ctypes.pointer(ctypes.py_object(hwnds))
        ctypes.windll.user32.EnumWindows(EnumWindowsProc(callback), lParam)
        return hwnds

    # 获取所有窗口句柄并打印
    all_handles = get_all_window_handles()
    for hwnd in all_handles:
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd) + 1
        buffer = ctypes.create_unicode_buffer(length)
        ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length)
        title = buffer.value if buffer.value else "No Title"
        # print(f"最小化Window handle: {hwnd}, Title: {title}")
        handles_mapping[title] = hwnd
    return handles_mapping


class FileLock:
    lockfile = os.path.join(current_directory, "app.lock")

    def __init__(self, lockfile=lockfile):
        self.lockfile = lockfile
        self.acquire()

    def acquire(self):
        if os.path.exists(self.lockfile):
            with open(self.lockfile, 'w') as f:
                f.write(str(os.getpid()))
            return False
        with open(self.lockfile, 'w') as f:
            f.write(str(os.getpid()))
        atexit.register(self.release)
        return True

    def release(self):
        os.remove(self.lockfile)

    @staticmethod
    def get_pid():
        if os.path.exists(FileLock.lockfile):
            try:
                with open(FileLock.lockfile, 'r') as f:
                    pid = int(f.read().strip())
                return pid
            except:
                return None
        else:
            return None

    @staticmethod
    def find_and_activate_window(window_title):
        """
        根据窗口名称激活窗口
        :param window_title:
        :return:
        """
        mapping = get_all_window_mapping()
        if window_title in mapping:
            hwnd = mapping[window_title]
            if hwnd:
                # 检查窗口是否最小化
                if ctypes.windll.user32.IsIconic(hwnd):
                    ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                    time.sleep(0.1)  # 增加一些延迟

                # 显示窗口
                ctypes.windll.user32.ShowWindow(hwnd, 5)  # SW_SHOW
                time.sleep(0.1)  # 增加一些延迟

                # 允许当前进程设置前台窗口
                ctypes.windll.user32.AllowSetForegroundWindow(ctypes.windll.kernel32.GetCurrentProcessId())

                # 将当前线程与窗口线程关联
                current_thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
                window_thread_id = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
                ctypes.windll.user32.AttachThreadInput(current_thread_id, window_thread_id, True)

                # 激活窗口
                ctypes.windll.user32.SetActiveWindow(hwnd)
                time.sleep(0.1)  # 增加一些延迟

                # 使用 PostMessage 发送激活消息
                ctypes.windll.user32.PostMessageW(hwnd, 0x0112, 0xF120, 0)  # WM_SYSCOMMAND, SC_RESTORE
                time.sleep(0.1)  # 增加一些延迟

                ctypes.windll.user32.SetForegroundWindow(hwnd)

                # 解除线程关联
                ctypes.windll.user32.AttachThreadInput(current_thread_id, window_thread_id, False)

                return True  # 找到目标窗口后停止枚举
            return False
        else:
            return False

    @staticmethod
    def is_pid_running(pid):
        """
        检查给定的 PID 是否正在运行。

        :param pid: 要检查的进程 ID
        :return: 如果 PID 正在运行，返回 True；否则返回 False
        """
        if pid is None:
            return False
        try:
            # 尝试获取进程信息
            process = psutil.Process(pid)
            # 如果进程存在，process 对象会被创建
            return True
        except psutil.NoSuchProcess:
            # 如果进程不存在，会抛出 NoSuchProcess 异常
            return False

    @staticmethod
    def kill_process_by_pid(pid):

        # 尝试第一种方式(linux)
        try:
            # 使用 taskkill 命令强制终止进程
            os.system(f"taskkill /F /PID {pid}")
            print(f"进程 {pid} 已被杀死")
        except Exception as e:
            print(f"杀死进程 {pid} 时发生错误：{e}")

        # 尝试第二种方式
        try:
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True)
            print(f"进程 {pid} 已被杀死")
            return True
        except subprocess.CalledProcessError as e:
            print(f"杀死进程 {pid} 时发生错误：{e}")

        # 尝试第三种方式
        try:
            process = psutil.Process(pid)
            process.terminate()  # 发送 SIGTERM 信号
            process.wait(timeout=5)  # 等待进程终止
            print(f"进程 {pid} 已被终止")
            return True
        except psutil.NoSuchProcess:
            print(f"进程 {pid} 不存在")
        except psutil.AccessDenied:
            print(f"没有权限杀死进程 {pid}")
        except Exception as e:
            print(f"杀死进程 {pid} 时发生错误：{e}")


# 创建文件夹
def create_fold_path(fold_path):
    if os.path.exists(fold_path) is False:
        os.makedirs(fold_path)


class DemoWindow(QWidget):
    def __init__(self):
        super(DemoWindow, self).__init__()
        self.setGeometry(100, 100, 300, 200)
        self.setWindowTitle(app_name)


app_name = "Demo Window"

if __name__ == "__main__":
    # 创建主循环
    app = QApplication()
    # 创建异步事件循环
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    # 锁定实例
    online = FileLock.is_pid_running(FileLock.get_pid())
    if online:
        FileLock.find_and_activate_window(app_name)
        sys.exit(0)
    else:
        # 创建文件锁
        lock = FileLock()

    # 创建窗口
    main_window = CSplashScreen(DemoWindow)
    # setup_main_theme(main_window)
    with loop:
        loop.run_forever()
