
import sys

from PySide6 import QtAsyncio, QtWidgets
from PySide6.QtWidgets import QApplication

from cocos_widgets.c_line_edit import CLineEdit


class DemoWidget(QtWidgets.QWidget):
    def __init__(self):
        super(DemoWidget, self).__init__()
        layout = QtWidgets.QVBoxLayout(self)

        line_edit1 = CLineEdit(text="输入",
                                place_holder_text="请输入",
                                radius=8,
                                border_size=2,
                                color="#FFF",  # 字体颜色
                                selection_color="#FFF",
                                bg_color="#333",
                                bg_color_active="#222",
                                context_color="#00ABE8")
        line_edit2 = CLineEdit(text="输入",
                                place_holder_text="请输入",
                                radius=8,
                                border_size=2,
                                color="#FFF",  # 字体颜色
                                selection_color="#FFF",
                                bg_color="#333",
                                bg_color_active="#222",
                                context_color="#00ABE8")
        line_edit1.setMinimumHeight(40)
        line_edit2.setMinimumHeight(40)
        layout.addWidget(line_edit1)
        layout.addWidget(line_edit2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
