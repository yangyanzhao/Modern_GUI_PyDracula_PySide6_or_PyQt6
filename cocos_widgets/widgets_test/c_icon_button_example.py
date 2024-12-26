import sys

from PySide6 import QtAsyncio, QtWidgets
from PySide6.QtWidgets import QWidget, QApplication

from cocos_widgets.c_icon_button import CIconButton


class DemoWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(500, 500)
        layout = QtWidgets.QVBoxLayout(self)

        c_credits = CIconButton(parent=self, app_parent=self, icon_path="calendar_fill.svg", tooltip_text="正常",
                                is_active=False)
        c_credits.clicked.connect(lambda: print(1))
        layout.addWidget(c_credits)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWindow()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
