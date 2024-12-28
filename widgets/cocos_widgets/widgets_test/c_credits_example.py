import sys

from PySide6 import QtAsyncio, QtWidgets
from PySide6.QtWidgets import QWidget, QApplication

from widgets.cocos_widgets.c_credits import CCredits


class DemoWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("CCredits")
        self.resize(500, 500)
        layout = QtWidgets.QVBoxLayout(self)

        c_credits = CCredits(
            copyright='By: Wanderson M. Pimenta',
            version='v1.0.0',
            bg_two='#343b48',
            font_family="Segoe UI",
            text_size=9,
            text_description_color='#4f5b6e',
            radius=8,
            padding=10,
        )
        layout.addWidget(c_credits)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWindow()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
