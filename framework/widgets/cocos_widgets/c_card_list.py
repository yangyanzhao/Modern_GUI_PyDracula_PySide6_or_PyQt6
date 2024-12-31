import sys

from PySide6 import QtWidgets, QtAsyncio
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from framework.widgets.dayu_widgets import MSwitch, MPushButton, MLabel, MTheme
from framework.widgets.dayu_widgets.mixin import hover_shadow_mixin, cursor_mixin


@hover_shadow_mixin
@cursor_mixin
class CPanMeta(QWidget):
    """
    包装器带边缘效果
    """

    def __init__(self, widget):
        super(CPanMeta, self).__init__()
        self.layout = QVBoxLayout(self)
        self.main_layout = QVBoxLayout()
        self.center_widget = QWidget()
        self.center_widget.setLayout(self.main_layout)

        self.main_layout.addWidget(widget)
        self.layout.addWidget(self.center_widget)


class CCardList(QtWidgets.QWidget):
    """
    卡片列表，带滑动条
    """

    def __init__(self, parent=None):
        super(CCardList, self).__init__(parent)
        # 初始化UI
        self.init_ui()

    def init_ui(self):
        right_lay = QtWidgets.QVBoxLayout()
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        task_widget = QtWidgets.QWidget()

        scroll.setWidget(task_widget)
        right_lay.addWidget(scroll)
        right_widget = QtWidgets.QWidget()
        right_widget.setLayout(right_lay)
        splitter = QtWidgets.QSplitter()
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 80)
        splitter.setStretchFactor(1, 20)
        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(splitter)
        self.setLayout(main_lay)

        self.task_card_lay = QtWidgets.QVBoxLayout()
        task_widget.setLayout(self.task_card_lay)

    def add_setting(self, widget):
        meta = CPanMeta(widget)
        self.task_card_lay.addWidget(meta)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = CCardList()
    demo_widget.add_setting(widget=MPushButton("单位"))
    demo_widget.add_setting(widget=MSwitch())
    demo_widget.add_setting(widget=MLabel("黑龙江中医药大学"))
    demo_widget.task_card_lay.addStretch()

    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
