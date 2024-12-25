import asyncio
import random
import sys

from PySide6 import QtAsyncio
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QApplication, QDialog, QFrame, QVBoxLayout, QWidget

from cocos_widgets.widgets_test.c_dialog.py_grips import PyGrips
from dayu_widgets import MPushButton

"""
弹窗包装器，用于将普通弹窗，包装成符合当前UI风格的边框和标题栏，标题栏位置可选择（默认为包装器顶部）。
"""


class FramelessDialogAbstract(QDialog):
    def __init__(self, has_title_bar=True, has_min_btn=True, has_max_btn=True, has_close_btn=True,
                 attach_title_bar_layout=None, parent=None):
        """
        窗口包装器
        :param has_title_bar: 是否带标题栏
        :param attach_title_bar_layout: 标题附着点（默认为包装器顶部）
        """
        super().__init__(parent)
        self.parent = parent
        self.has_title_bar = has_title_bar
        self.attach_title_bar_layout = attach_title_bar_layout
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.center_widget = QWidget()
        self.center_widget.setObjectName("center_widget")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.center_widget)

        # 标题栏
        if self.has_title_bar:
            # 自定义标题栏
            self.title_bar_frame = QFrame()
            self.title_bar_frame.setMinimumHeight(40)
            self.title_bar_frame.setMaximumHeight(40)
            self.title_bar_layout = QVBoxLayout(self.title_bar_frame)
            self.title_bar_layout.setContentsMargins(0, 0, 0, 0)
            # 标题栏
            self.title_bar = PyTitleBar(
                self,
                app_parent=self,
                logo_width=100,
                logo_image="logo_top_100x22.svg",
                bg_color=self.themes["app_color"]["bg_two"],
                div_color=self.themes["app_color"]["bg_three"],
                btn_bg_color=self.themes["app_color"]["bg_two"],
                btn_bg_color_hover=self.themes["app_color"]["bg_three"],
                btn_bg_color_pressed=self.themes["app_color"]["bg_one"],
                icon_color=self.themes["app_color"]["icon_color"],
                icon_color_hover=self.themes["app_color"]["icon_hover"],
                icon_color_pressed=self.themes["app_color"]["icon_pressed"],
                icon_color_active=self.themes["app_color"]["icon_active"],
                context_color=self.themes["app_color"]["context_color"],
                dark_one=self.themes["app_color"]["dark_one"],
                text_foreground=self.themes["app_color"]["text_foreground"],
                radius=8,
                radius_corners=[1, 2, 3, 4] if self.attach_title_bar_layout else [1, 2],
                font_family=self.settings["font"]["family"],
                title_size=self.settings["font"]["title_size"],
                is_custom_title_bar=self.settings["custom_title_bar"],
                is_custom_title_min_btn=has_min_btn,
                is_custom_title_max_btn=has_max_btn,
                is_custom_title_close_btn=has_close_btn,
                is_show_datetime=False,
            )
            self.title_bar_layout.addWidget(self.title_bar)
            if self.attach_title_bar_layout is None:
                self.layout.insertWidget(0, self.title_bar_frame)
            else:
                self.attach_title_bar_layout.insertWidget(0, self.title_bar_frame)

        style = f"""
                #center_widget {{
                    border-bottom-left-radius: 10px;
                    border-bottom-right-radius: 10px;
                    background-color: '{self.themes["app_color"]["bg_three"]}';
                }}
                """ if self.has_title_bar and not self.attach_title_bar_layout else f"""
                #center_widget {{
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                    border-bottom-left-radius: 10px;
                    border-bottom-right-radius: 10px;
                    background-color: '{self.themes["app_color"]["bg_three"]}';
                }}
                """
        self.center_widget.setStyleSheet(style)
        self.center_layout = QVBoxLayout(self)
        self.center_layout.setContentsMargins(5, 5, 5, 5)
        # self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setSpacing(0)
        self.center_widget.setLayout(self.center_layout)

        # 调整边缘缩放
        self.hide_grips = True  # 显示/隐藏调整大小边缘点
        self.left_grip = PyGrips(self, "left", self.hide_grips)
        self.right_grip = PyGrips(self, "right", self.hide_grips)
        self.top_grip = PyGrips(self, "top", self.hide_grips)
        self.bottom_grip = PyGrips(self, "bottom", self.hide_grips)
        self.top_left_grip = PyGrips(self, "top_left", self.hide_grips)
        self.top_right_grip = PyGrips(self, "top_right", self.hide_grips)
        self.bottom_left_grip = PyGrips(self, "bottom_left", self.hide_grips)
        self.bottom_right_grip = PyGrips(self, "bottom_right", self.hide_grips)

        self.adjustSize()
        self.show_centered()

    def resizeEvent(self, e):
        # 背景图片跟随缩放
        # self.update_background()
        super().resizeEvent(e)
        self.left_grip.setGeometry(0, 10, 10, self.height() - 5)
        self.right_grip.setGeometry(self.width() - 10, 0, 10, self.height() + 5)
        self.top_grip.setGeometry(5, 0, self.width() - 10, 10)
        self.bottom_grip.setGeometry(0, self.height() - 10, self.width() - 10, 10)

        self.top_left_grip.setGeometry(0, 0, 15, 15)
        self.top_right_grip.setGeometry(self.width() - 15, 0, 15, 15)
        self.bottom_left_grip.setGeometry(0, self.height() - 15, 15, 15)
        self.bottom_right_grip.setGeometry(self.width() - 15, self.height() - 15, 15, 15)

    # 鼠标点击事件
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

    def show_centered(self):
        if self.parent:
            # 获取父窗口的几何信息
            parent_rect = self.parent.geometry()
            # 获取子窗口的几何信息
            self_rect = self.geometry()
            # 计算子窗口应该移动到的位置
            x = parent_rect.center().x() - self_rect.width() // 2
            y = parent_rect.center().y() - self_rect.height() // 2
            # 移动子窗口
            self.move(x, y + random.randint(-20, 20))
        self.show()


class DemoWindow(FramelessDialogAbstract):
    def __init__(self, parent=None):
        super(DemoWindow, self).__init__(has_title_bar=True, parent=parent)
        q_widget = QWidget()

        layout = QVBoxLayout(q_widget)
        button1 = MPushButton("BTN1")
        button2 = MPushButton("BTN2")
        button3 = MPushButton("BTN3")
        layout.addWidget(button1)
        layout.addWidget(button2)
        layout.addWidget(button3)
        self.center_layout.addWidget(q_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWindow()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)