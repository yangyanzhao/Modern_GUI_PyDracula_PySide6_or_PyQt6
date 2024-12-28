import sys

from PySide6 import QtAsyncio
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication

from framework.widgets.cocos_widgets.c_slider import CSlider


class DemoWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(DemoWindow, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(self)
        self.labelValue = QLabel(self)
        layout.addWidget(self.labelValue)
        v_slider = CSlider(orientation=Qt.Vertical, parent=self)
        v_slider.valueChanged.connect(lambda v: self.labelValue.setText(str(v)))
        layout.addWidget(v_slider)
        h_slider = CSlider(orientation=Qt.Horizontal, parent=self)
        h_slider.valueChanged.connect(lambda v: self.labelValue.setText(str(v)))
        layout.addWidget(h_slider)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWindow()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)