import sys

from PySide6 import QtAsyncio
from PySide6.QtWidgets import QApplication, QWidget
from framework.widgets.dayu_widgets.qt import MIcon
from framework.widgets.dayu_widgets import MTheme, MFlowLayout, MPushButton
class DemoWidget(QWidget):
    def __init__(self, parent=None):
        super(DemoWidget, self).__init__(parent)
        layout = MFlowLayout()
        self.setLayout(layout)
        for i in range(10):
            self.layout().addWidget(MPushButton(icon=MIcon("add_line.svg")))
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    MTheme().apply(demo_widget)
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)