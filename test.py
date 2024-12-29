import sys

from PySide6 import QtAsyncio
from PySide6.QtWidgets import QApplication

from framework.widgets.dayu_widgets import MComboBox, MMenu

if __name__ == '__main__':
    app = QApplication(sys.argv)

    combo_box = MComboBox().small()
    combo_box.show()
    menu = MMenu(parent=combo_box)
    menu.set_data([1, 2, 3])
    combo_box.set_menu(menu)
    # 显示窗口
    QtAsyncio.run(handle_sigint=True)
