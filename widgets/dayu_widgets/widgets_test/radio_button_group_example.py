import functools
import random
import sys

from PySide6 import QtAsyncio
from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout
from widgets.dayu_widgets.qt import MIcon

from widgets.dayu_widgets import MTheme, MPushButton,MRadioButtonGroup, MFieldMixin, MLabel
class DemoWidget(QWidget, MFieldMixin):
    def __init__(self, parent=None):
        super(DemoWidget, self).__init__(parent)
        self.setWindowTitle("MLoading控件学习")
        # 布局
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        radio_button_group = MRadioButtonGroup()
        radio_button_group.set_button_list(
            [{"text": "Apple", "checked": True, "icon": MIcon("app-maya.png")}, {"text": "Banana"}, {"text": "Pear"}])
        radio_button_group.add_button({"text": "Orange"})
        # 注册一个普通属性
        self.register_field("radio_checked", -1)
        # 双向绑定
        self.bind(data_name="radio_checked", widget=radio_button_group, qt_property="dayu_checked",
                  signal='sig_checked_changed', callback=lambda: print("触发回调"))
        # 注册一个计算属性,用来显示选中的值
        self.register_field(name="value", getter=functools.partial(lambda: radio_button_group.get_dayu_checked()))
        label = MLabel()
        # 单向绑定
        self.bind(data_name='value', widget=label, qt_property='text')
        button = MPushButton(text="change value", clicked=functools.partial(lambda: self.set_field("radio_checked", random.randint(-1, 2))))
        self.main_layout.addWidget(radio_button_group)
        self.main_layout.addWidget(label)
        self.main_layout.addWidget(button)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    MTheme().apply(demo_widget)
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)