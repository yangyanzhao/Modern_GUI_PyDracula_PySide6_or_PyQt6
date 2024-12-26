import sys

from PySide6 import QtAsyncio, QtWidgets
from PySide6.QtWidgets import QWidget, QApplication

from cocos_widgets.c_circular_progress import CCircularProgress
from cocos_widgets.c_window.c_window import CWindow


class DemoWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("PyCircularProgress")
        self.resize(500, 500)
        layout = QtWidgets.QVBoxLayout(self)

        self.c_window = CWindow(parent=self)
        custom_title_bar = False
        if custom_title_bar:
            self.c_window.set_stylesheet(border_radius=0, border_size=0)
        layout.addWidget(self.c_window)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWindow()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
