import sys

from PySide6 import QtAsyncio, QtWidgets
from PySide6.QtWidgets import QWidget, QApplication

from framework.widgets.cocos_widgets.c_left_column.c_left_column import CLeftColumn
from framework.widgets.cocos_widgets.c_left_column.c_left_column_info import CLeftColumnInfo


class DemoWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(500, 500)
        layout = QtWidgets.QVBoxLayout(self)

        c_left_column = CLeftColumn(
            parent=self,
            app_parent=self,
            text_title="Settings Left Frame",
            text_title_size=10,
            text_title_color='#8a95aa',
            icon_path='icon_settings.svg',
            dark_one='#1b1e23',
            bg_color='#3c4454',
            btn_color='#3c4454',
            btn_color_hover='#343b48',
            btn_color_pressed='#2c313c',
            icon_color='#c3ccdf',
            icon_color_hover='#dce1ec',
            context_color='#568af2',
            icon_color_pressed='#6c99f4',
            icon_close_path='icon_close.svg'
        )
        layout.addWidget(c_left_column)
        c_left_column_info = CLeftColumnInfo(
            parent=self,
            app_parent=self,
            text_title="Settings Left Frame",
            text_title_size=10,
            text_title_color='#8a95aa',
            icon_path='icon_settings.svg',
            dark_one='#1b1e23',
            bg_color='#3c4454',
            btn_color='#3c4454',
            btn_color_hover='#343b48',
            btn_color_pressed='#2c313c',
            icon_color='#c3ccdf',
            icon_color_hover='#dce1ec',
            context_color='#568af2',
            icon_color_pressed='#6c99f4',
            icon_close_path='icon_close.svg'
        )
        layout.addWidget(c_left_column_info)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWindow()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
