# 学习笔记 MLineEdit控件
import sys

from PySide6 import QtAsyncio
from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout
from widgets.dayu_widgets.qt import MIcon

from widgets.dayu_widgets import MTheme, MRadioButton


class DemoWidget(QWidget):
    def __init__(self, parent=None):
        super(DemoWidget, self).__init__(parent)
        self.setWindowTitle("MLoading控件学习")
        # 布局
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        lay_1 = QHBoxLayout()
        lay_1.addWidget(MRadioButton("Maya"))
        lay_1.addWidget(MRadioButton("Nuke"))
        lay_1.addWidget(MRadioButton("Houdini"))
        self.main_layout.addLayout(lay_1)

        check_box_icon_1 = MRadioButton("Folder")
        check_box_icon_1.setIcon(MIcon("folder_fill.svg"))
        check_box_icon_2 = MRadioButton("Media")
        check_box_icon_2.setIcon(MIcon("media_fill.svg"))
        check_box_icon_2.setChecked(True)
        check_box_icon_3 = MRadioButton("User")
        check_box_icon_3.setIcon(MIcon("user_fill.svg"))
        check_box_icon_3.setEnabled(False)
        lay_2 = QHBoxLayout()
        lay_2.addWidget(check_box_icon_1)
        lay_2.addWidget(check_box_icon_2)
        lay_2.addWidget(check_box_icon_3)
        self.main_layout.addLayout(lay_2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    MTheme().apply(demo_widget)
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)