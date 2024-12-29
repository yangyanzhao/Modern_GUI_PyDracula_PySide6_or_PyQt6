import sys

from PySide6 import QtAsyncio
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication

from framework.widgets.dayu_widgets import MTheme, MLineEdit, MComboBox, MMenu


class DemoWidget(QWidget):
    def __init__(self, parent=None):
        super(DemoWidget, self).__init__(parent)
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        line_edit = MLineEdit()
        combobox = MComboBox()
        option_menu = MMenu()
        option_menu.set_separator("|")
        option_menu.set_data([r"http://", r"https://"])
        combobox.set_menu(option_menu)
        combobox.set_value("http://")
        combobox.setFixedWidth(80)
        line_edit.set_prefix_widget(combobox)
        layout.addWidget(line_edit)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
