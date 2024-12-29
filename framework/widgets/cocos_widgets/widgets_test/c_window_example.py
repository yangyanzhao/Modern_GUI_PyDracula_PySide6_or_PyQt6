import sys

from PySide6 import QtAsyncio, QtWidgets
from PySide6.QtWidgets import QWidget, QApplication, QMainWindow

from framework.widgets.cocos_widgets import CTitleBar
from framework.widgets.cocos_widgets.c_window.c_window import CWindow


class DemoWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(500, 500)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)

        self.c_window = CWindow(parent=self, bg_color="#2c31FF", border_color="#343bFF", enable_shadow=True)
        custom_title_bar = False
        if custom_title_bar:
            self.c_window.set_stylesheet(border_radius=0, border_size=0)
        layout.addWidget(self.c_window)

        self.c_title_bar = CTitleBar(parent=self, app_parent=self)
        self.c_title_bar.setFixedHeight(40)
        # layout.insertWidget(0, self.c_title_bar)

    def mousePressEvent(self, event):
        super(DemoWindow, self).mousePressEvent(event)
        self.dragPos = event.globalPosition().toPoint()  # 使用 globalPosition().toPoint()


class DemoWindowPlus(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("PyCircularProgress")
        self.resize(500, 500)

        self.c_window = CWindow(parent=self)
        custom_title_bar = True
        if custom_title_bar:
            self.c_window.set_stylesheet(border_radius=0, border_size=0)
        self.setCentralWidget(self.c_window)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWindow()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
