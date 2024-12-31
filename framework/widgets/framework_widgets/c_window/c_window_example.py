import sys

from PySide6 import QtAsyncio
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QWidget, QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QCheckBox

from framework.widgets.cocos_widgets import CTitleBar, CGrips
from framework.widgets.dayu_widgets import MPushButton, MLineEdit, MCheckBox, MTheme, MComboBox, MMenu
from framework.widgets.framework_widgets.c_window.c_window import CWindow


class DemoWindow01(QWidget):
    """
    自定义窗口
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(500, 500)
        # 隐藏标题栏
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        # 设置背景透明
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        # 设置自定义窗口背景控件
        self.c_window = CWindow(parent=self, bg_color="#2c313c", border_color="#343b48", enable_shadow=True)
        self.c_window.set_stylesheet(border_top_left_radius=10, border_top_right_radius=10,
                                     border_bottom_left_radius=10,
                                     border_bottom_right_radius=10, border_size=0)
        layout.addWidget(self.c_window)


class DemoWindow02(QWidget):
    """
    自定义窗口+边缘缩放
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(500, 500)
        self.setMinimumSize(QSize(100, 100))
        # 隐藏标题栏
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        # 设置背景透明
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        # 设置自定义窗口背景控件
        self.c_window = CWindow(parent=self, bg_color="#2c313c", border_color="#343b48", enable_shadow=True)
        self.c_window.set_stylesheet(border_top_left_radius=10, border_top_right_radius=10,
                                     border_bottom_left_radius=10,
                                     border_bottom_right_radius=10, border_size=0)
        layout.addWidget(self.c_window)

        # 边缘缩放
        disable_color = True
        self.top_grip = CGrips(parent=self, position="top", disable_color=disable_color)
        self.bottom_grip = CGrips(self, "bottom", disable_color=disable_color)
        self.left_grip = CGrips(self, "left", disable_color=disable_color)
        self.right_grip = CGrips(self, "right", disable_color=disable_color)
        self.top_left_grip = CGrips(self, "top_left", disable_color=disable_color)
        self.top_right_grip = CGrips(self, "top_right", disable_color=disable_color)
        self.bottom_left_grip = CGrips(self, "bottom_left", disable_color=disable_color)
        self.bottom_right_grip = CGrips(self, "bottom_right", disable_color=disable_color)

    def resizeEvent(self, event):
        # 边缘缩放
        self.left_grip.setGeometry(0, 10, 10, self.height())
        self.right_grip.setGeometry(self.width() - 10, 10, 10, self.height())
        self.top_grip.setGeometry(0, 0, self.width(), 10)
        self.bottom_grip.setGeometry(0, self.height() - 10, self.width(), 10)

        self.top_left_grip.setGeometry(5, 5, 20, 20)
        self.top_right_grip.setGeometry(self.width() - 25, 5, 20, 20)
        self.bottom_left_grip.setGeometry(5, self.height() - 25, 20, 20)
        self.bottom_right_grip.setGeometry(self.width() - 25, self.height() - 25, 20, 20)


class DemoWindow03(QWidget):
    """
    自定义窗口+自定义标题栏+边缘缩放+窗口移动
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(500, 500)
        # 隐藏标题栏
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        # 设置背景透明
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        # 设置自定义窗口背景控件
        self.c_window = CWindow(parent=self, bg_color="#2c313c", border_color="#343b48", enable_shadow=True)
        self.c_window.set_stylesheet(border_top_left_radius=0, border_top_right_radius=0, border_bottom_left_radius=10,
                                     border_bottom_right_radius=10, border_size=0)
        layout.addWidget(self.c_window)

        # 自定义标题栏
        self.c_title_bar = CTitleBar(parent=self, app_parent=self)
        self.c_title_bar.setFixedHeight(40)
        layout.insertWidget(0, self.c_title_bar)

        # 边缘缩放
        disable_color = True
        self.top_grip = CGrips(parent=self, position="top", disable_color=disable_color)
        self.bottom_grip = CGrips(self, "bottom", disable_color=disable_color)
        self.left_grip = CGrips(self, "left", disable_color=disable_color)
        self.right_grip = CGrips(self, "right", disable_color=disable_color)
        self.top_left_grip = CGrips(self, "top_left", disable_color=disable_color)
        self.top_right_grip = CGrips(self, "top_right", disable_color=disable_color)
        self.bottom_left_grip = CGrips(self, "bottom_left", disable_color=disable_color)
        self.bottom_right_grip = CGrips(self, "bottom_right", disable_color=disable_color)

    def mousePressEvent(self, event):
        """
        窗口移动
        :param event:
        :return:
        """
        super().mousePressEvent(event)
        self.dragPos = event.globalPosition().toPoint()  # 使用 globalPosition().toPoint()

    def resizeEvent(self, event):
        # 边缘缩放
        self.left_grip.setGeometry(0, 10, 10, self.height())
        self.right_grip.setGeometry(self.width() - 10, 10, 10, self.height())
        self.top_grip.setGeometry(0, 0, self.width(), 10)
        self.bottom_grip.setGeometry(0, self.height() - 10, self.width(), 10)

        self.top_left_grip.setGeometry(5, 5, 20, 20)
        self.top_right_grip.setGeometry(self.width() - 25, 5, 20, 20)
        self.bottom_left_grip.setGeometry(5, self.height() - 25, 20, 20)
        self.bottom_right_grip.setGeometry(self.width() - 25, self.height() - 25, 20, 20)


class DemoWindow04(QWidget):
    """
    自定义窗口+自定义标题栏+边缘缩放+窗口移动+登录表单
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(500, 500)
        # 隐藏标题栏
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        # 设置背景透明
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        # 设置自定义窗口背景控件
        self.c_window = CWindow(parent=self, bg_color="#FFF", border_color="#343b48", layout=Qt.Orientation.Vertical,
                                enable_shadow=True)
        self.c_window.set_stylesheet(border_top_left_radius=0, border_top_right_radius=0, border_bottom_left_radius=10,
                                     border_bottom_right_radius=10, border_size=0)
        layout.addWidget(self.c_window)

        # 自定义标题栏
        self.c_title_bar = CTitleBar(parent=self, app_parent=self)
        self.c_title_bar.setFixedHeight(40)
        layout.insertWidget(0, self.c_title_bar)

        # 边缘缩放
        disable_color = True
        self.top_grip = CGrips(parent=self, position="top", disable_color=disable_color)
        self.bottom_grip = CGrips(self, "bottom", disable_color=disable_color)
        self.left_grip = CGrips(self, "left", disable_color=disable_color)
        self.right_grip = CGrips(self, "right", disable_color=disable_color)
        self.top_left_grip = CGrips(self, "top_left", disable_color=disable_color)
        self.top_right_grip = CGrips(self, "top_right", disable_color=disable_color)
        self.bottom_left_grip = CGrips(self, "bottom_left", disable_color=disable_color)
        self.bottom_right_grip = CGrips(self, "bottom_right", disable_color=disable_color)

        # 业务UI
        self.init_UI()

    def mousePressEvent(self, event):
        """
        窗口移动
        :param event:
        :return:
        """
        super().mousePressEvent(event)
        self.dragPos = event.globalPosition().toPoint()  # 使用 globalPosition().toPoint()

    def resizeEvent(self, event):
        # 边缘缩放
        self.left_grip.setGeometry(0, 10, 10, self.height())
        self.right_grip.setGeometry(self.width() - 10, 10, 10, self.height())
        self.top_grip.setGeometry(0, 0, self.width(), 10)
        self.bottom_grip.setGeometry(0, self.height() - 10, self.width(), 10)

        self.top_left_grip.setGeometry(5, 5, 20, 20)
        self.top_right_grip.setGeometry(self.width() - 25, 5, 20, 20)
        self.bottom_left_grip.setGeometry(5, self.height() - 25, 20, 20)
        self.bottom_right_grip.setGeometry(self.width() - 25, self.height() - 25, 20, 20)

    def init_UI(self):
        """
        业务UI初始化
        :return:
        """

        class BusinessWidget(QWidget):
            """
            # 业务控件
            """

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.setObjectName("business_widget")
                login_form_layout = QVBoxLayout(self)

                edit_username = MLineEdit()
                edit_username.setPlaceholderText("请输入账号")
                edit_password = MLineEdit()
                edit_password.setEchoMode(QLineEdit.EchoMode.Password)
                edit_password.setPlaceholderText("请输入密码")
                combobox = MComboBox()
                combobox.set_placeholder("请选择城市")
                menu = MMenu()
                menu.set_data(["北京", "上海", "广州", "深圳"])
                combobox.set_menu(menu)
                button = MPushButton("登录")

                login_form_layout.addWidget(edit_username)
                login_form_layout.addWidget(edit_password)
                login_form_layout.addWidget(combobox)
                login_form_layout.addWidget(button)
                login_form_layout.addStretch()

        self.c_window.layout.addWidget(BusinessWidget())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWindow04()
    MTheme('dark').apply(demo_widget)
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
