import sys

from PySide6 import QtWidgets, QtAsyncio
from PySide6.QtWidgets import QApplication

from framework.widgets.dayu_widgets import MTheme, MSwitch, MSlider, MLabel, MCarousel
from framework.widgets.dayu_widgets.qt import MPixmap


class DemoWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(DemoWidget, self).__init__(parent)
        self.setWindowTitle("Examples for MCarousel")
        self._init_ui()

    def _init_ui(self):
        switch = MSwitch()
        switch.setChecked(True)
        slider = MSlider()
        slider.setRange(1, 10)
        switch_lay = QtWidgets.QFormLayout()
        switch_lay.addRow(MLabel("AutoPlay"), switch)
        switch_lay.addRow(MLabel("Interval"), slider)
        test = MCarousel(
            [MPixmap("app-{}.png".format(a)) for a in ["maya", "nuke", "houdini"]],
            width=300,
            height=300,
            autoplay=True,
        )
        switch.toggled.connect(test.set_autoplay)
        slider.valueChanged.connect(lambda x: test.set_interval(x * 1000))
        slider.setValue(3)

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(test)
        main_lay.addLayout(switch_lay)
        main_lay.addStretch()
        self.setLayout(main_lay)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    MTheme().apply(demo_widget)
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
