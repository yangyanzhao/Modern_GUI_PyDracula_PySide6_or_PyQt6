import sys

from PySide6 import QtAsyncio
from PySide6.QtWidgets import QApplication

from cocos_widgets.c_card_list import MCardList
from dayu_widgets import MSwitch, MPushButton, MLabel, MTheme


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = MCardList()
    demo_widget.add_setting(widget=MPushButton("单位"))
    demo_widget.add_setting(widget=MSwitch())
    demo_widget.add_setting(widget=MLabel("黑龙江中医药大学"))
    demo_widget.task_card_lay.addStretch()

    MTheme().apply(demo_widget)
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
