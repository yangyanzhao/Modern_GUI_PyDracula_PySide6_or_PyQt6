from PySide6 import QtWidgets
from dayu_widgets import MTheme, MAlert
import sys
from PySide6.QtWidgets import QApplication
from PySide6 import QtAsyncio


class DemoWidget(QtWidgets.QWidget):
    def __init__(self):
        super(DemoWidget, self).__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(MAlert("Hello World").success())
        layout.addWidget(MAlert("Hello World").info())
        layout.addWidget(MAlert("Hello World").error())
        layout.addWidget(MAlert("Hello World").warning().closable())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    MTheme().apply(demo_widget)
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
