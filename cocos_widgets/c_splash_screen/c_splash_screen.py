import asyncio
import logging
import time

import qasync
from PySide6 import QtCore
from PySide6.QtCore import QTimer
from PySide6.QtGui import (QColor)
from PySide6.QtWidgets import *

from cocos_widgets.c_splash_screen.ui_main import Ui_MainWindow
from cocos_widgets.c_splash_screen.ui_splash_screen import Ui_SplashScreen
from db.pickle_db.data_storage_service import data_session_storage_py_one_dark, data_local_storage_py_one_dark


def increase_counter(destination: str):
    logging.info(destination)
    data_session_storage_py_one_dark.set("progress_widget_real_time", destination)
    current_counter = int(data_session_storage_py_one_dark.get("progress_counter", none_or_else=0))
    current_counter += 1
    data_session_storage_py_one_dark.set("progress_counter", current_counter)
    window_count = data_local_storage_py_one_dark.get("window_count", none_or_else=1)  # 窗口总数
    current_progress_counter_real_time = data_session_storage_py_one_dark.get("progress_counter_real_time",
                                                                              none_or_else=0)
    if current_counter >= window_count:
        # 在没有计算出窗口总数的情况下，无法计算出准确的进度比，只好采取累计进度。
        data_session_storage_py_one_dark.set("progress_counter_real_time", current_progress_counter_real_time + 1)
    else:
        progress_counter_real_time = int(current_counter * 100 / window_count)  # 需要抵达的进度
        if progress_counter_real_time >= 100:
            progress_counter_real_time = 100

        # print(f"计算:{current_counter}*100/{window_count}")
        # print(f"需要抵達:{progress_counter_real_time}")

        def go_to_progress(current, progress):
            # 循环+1的形式赋值
            for i in range(100):
                time.sleep(0.1)
                current += 1
                data_session_storage_py_one_dark.set("progress_counter_real_time", current)
                if current >= progress:
                    break

        go_to_progress(current_progress_counter_real_time, progress_counter_real_time)


# SPLASH SCREEN
class CSplashScreen(QMainWindow):
    def __init__(self, main_window_class, parent=None):
        super(CSplashScreen, self).__init__(parent)
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)
        self.ui.label_description.setText("<strong>WELCOME</strong> TO MY APPLICATION")
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)
        self.init_not_first(main_window_class)
        self.show()

    def init_not_first(self, main_window_class):
        self.main_window_class = main_window_class
        # 异步初始化
        QTimer.singleShot(1000, self.init_main_class)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        self.timer.start(100)

    def progress(self):
        # SET VALUE TO PROGRESS BAR
        counter = data_session_storage_py_one_dark.get("progress_counter")
        if counter is None:
            data_session_storage_py_one_dark.set("progress_counter", 0)
        # 窗口总数量
        data_session_storage_py_one_dark.widget_bind_value(widget=self.ui.progressBar,
                                                           session_field_name="progress_counter_real_time",
                                                           widget_property="value")
        # 窗口总数量
        data_session_storage_py_one_dark.widget_bind_value(widget=self.ui.label_credits,
                                                           session_field_name="progress_widget_real_time",
                                                           widget_property="text")

        # 如果已经初始化完毕，则直接设置为100
        if hasattr(self, 'main'):
            # 存储窗口的数量到LocalStorage
            data_local_storage_py_one_dark.set("window_count", data_session_storage_py_one_dark.get('progress_counter'))
            # 如果此时的进度条还没有走完，则补充一下
            current_progress_counter_real_time = data_session_storage_py_one_dark.get("progress_counter_real_time", 0)
            if current_progress_counter_real_time < 100:
                # 循环+1的形式赋值
                for i in range(100):
                    time.sleep(0.001)
                    current_progress_counter_real_time += 1
                    data_session_storage_py_one_dark.set("progress_counter_real_time",
                                                         current_progress_counter_real_time)
                    if current_progress_counter_real_time >= 100:
                        break
            self.timer.stop()
            self.main.show()
            self.close()
        if self.ui.progressBar.value() >= 100:
            self.timer.stop()
            self.main.show()
            self.close()

    def init_main_class(self):
        self.main = self.main_window_class()
        # 存储指针到全局变量中


# YOUR APPLICATION
class DemoWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        increase_counter("DemoWindow")  # 需要初始的窗口记入进度即可。
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


if __name__ == "__main__":
    # 创建主循环
    app = QApplication()

    # 创建异步事件循环
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    main_window = CSplashScreen(DemoWindow)
    with loop:
        loop.run_forever()
