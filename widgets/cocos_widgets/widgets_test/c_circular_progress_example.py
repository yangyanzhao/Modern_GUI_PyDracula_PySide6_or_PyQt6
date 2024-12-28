import sys

from PySide6 import QtAsyncio, QtWidgets
from PySide6.QtWidgets import QWidget, QApplication

from widgets.cocos_widgets.c_circular_progress import CCircularProgress


class DemoWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("PyCircularProgress")
        self.resize(500, 500)
        layout = QtWidgets.QVBoxLayout(self)

        self.circular_progress = CCircularProgress(
            value=90,
            progress_width=20,
            is_rounded=True,
            max_value=100,
            progress_color="#ff79c6",
            enable_text=True,
            font_family="Segoe UI",
            font_size=32,
            suffix="%",
            text_color="BLUE",
            enable_bg=True,
            bg_color="#44475a"
        )

        layout.addWidget(self.circular_progress)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWindow()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
