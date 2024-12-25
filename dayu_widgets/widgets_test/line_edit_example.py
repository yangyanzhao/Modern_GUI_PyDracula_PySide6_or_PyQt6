# 学习笔记 MLineEdit控件
import asyncio
import sys

from PySide6 import QtAsyncio
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from dayu_widgets.qt import MIcon, MIconWidget

from dayu_widgets import MTheme, MPushButton, MLineEdit


class DemoWidget(QWidget):
    def __init__(self, parent=None):
        super(DemoWidget, self).__init__(parent)
        self.setWindowTitle("MLoading控件学习")
        # 布局
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # 大小输入框
        self.sub_layout_1 = QHBoxLayout()
        self.main_layout.addLayout(self.sub_layout_1)
        self.sub_layout_1.addWidget(MLineEdit("巨型输入框").huge())
        self.sub_layout_1.addWidget(MLineEdit("大型输入框").large())
        self.sub_layout_1.addWidget(MLineEdit("默认输入框"))
        self.sub_layout_1.addWidget(MLineEdit("小型输入框").small())
        self.sub_layout_1.addWidget(MLineEdit("微型输入框").tiny())

        # 添加带图标输入框
        self.sub_layout_2 = QHBoxLayout()
        self.main_layout.addLayout(self.sub_layout_2)
        m_line_edit = MLineEdit("上传按钮")
        m_line_edit.set_prefix_widget(MIconWidget(icon="folder_line.svg", color="#ddd"))
        self.sub_layout_2.addWidget(m_line_edit)
        self.sub_layout_2.addWidget(MPushButton("文件按钮", MIcon("folder_line.svg", "#ddd")).primary())
        self.sub_layout_2.addWidget(MPushButton("提交按钮", MIcon("success_line.svg", "#ddd")).success())
        self.sub_layout_2.addWidget(MPushButton("编辑按钮", MIcon("edit_line.svg", "#ddd")).warning())
        self.sub_layout_2.addWidget(MPushButton("删除按钮", MIcon("trash_line.svg", "#ddd")).danger())

        # 按钮大小
        self.sub_layout_3 = QHBoxLayout()
        self.main_layout.addLayout(self.sub_layout_3)
        self.sub_layout_3.addWidget(MPushButton("大型按钮").large())
        self.sub_layout_3.addWidget(MPushButton("中型按钮").medium().primary())
        self.sub_layout_3.addWidget(MPushButton("小型按钮").small().primary())
        self.sub_layout_3.addWidget(MPushButton("微型按钮").tiny().primary())

        # 禁用按钮
        self.sub_layout_4 = QHBoxLayout()
        self.main_layout.addLayout(self.sub_layout_4)
        disabled_button_1 = MPushButton("禁用按钮")
        disabled_button_1.setEnabled(False)
        self.sub_layout_4.addWidget(disabled_button_1)

        # 自定义图标、自定义颜色
        self.sub_layout_5 = QHBoxLayout()
        self.main_layout.addLayout(self.sub_layout_5)
        self.sub_layout_5.addWidget(MPushButton("自定义颜色按钮").custom_color("#FFFFFF"))
        # 将自定义的图标文件放置在dayu_widgets/static资源文件夹中，然后引用即可。
        self.sub_layout_5.addWidget(MPushButton("自定义图标按钮", MIcon("图标.png", "#ddd")))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    MTheme().apply(demo_widget)
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)