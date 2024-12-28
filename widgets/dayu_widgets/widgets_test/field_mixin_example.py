import random
from widgets.dayu_widgets import MTheme, MPushButton, MFieldMixin, MLineEdit
import sys

from PySide6 import QtAsyncio
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout


class DemoWidget(QWidget, MFieldMixin):
    def __init__(self, parent=None):
        super(DemoWidget, self).__init__(parent)
        # 布局
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        """普通属性的双向绑定示例:"""
        self.button_props = MPushButton("Click Props")
        self.button_props.clicked.connect(self.on_click_props)
        self.main_layout.addWidget(self.button_props)

        self.edit_props = MLineEdit("Props")
        self.main_layout.addWidget(self.edit_props)

        # 注册一个数据属性,通常不需要getter，因为数据属性是绑定在UI控件上的，所以会自动更新。
        self.register_field(name='Props', setter=lambda value: self.set_field('Props', value))
        # 将数据绑定到UI控件上，当数据发生改变，则更新UI,并触发callback回调。当signal信号触发，则更新UI数据到数据属性，因数据属性发生改变，所以也会触发callback回调。
        self.bind(data_name="Props", widget=self.edit_props, qt_property="text",
                  signal="sig_delay_text_changed", callback=lambda: print(f"[普通]触发回调函数{self.field('Props')}"))
        """计算属性的单向绑定示例:"""
        self.button_computed = MPushButton("Click Computed")
        self.button_computed.clicked.connect(self.on_click_computed)
        self.main_layout.addWidget(self.button_computed)
        self.edit_computed = MLineEdit("Computed")
        self.main_layout.addWidget(self.edit_computed)
        # 注册一个计算属性，通常不需要setter，因为计算属性都是由其他数据计算出来的，不需要手动设置。
        self.register_field(name='Computed', getter=lambda: self.field('Props') * 2 if self.field('Props') else 0)
        # 将数据绑定到UI控件上，当数据发生改变，则更新UI,并触发callback回调函数。通常不需要signal，因为计算属性是自动更新的。
        self.bind(data_name="Computed", widget=self.edit_computed, qt_property="text",
                  callback=lambda: print(f"[计算]触发回调函数{self.field('Computed')}"))

    def on_click_props(self):
        print(self.field('Props'))
        self.set_field(name='Props', value=f"{random.randint(-100, 100)}")

    def on_click_computed(self):
        print(self.field('Computed'))
        self.set_field('Props', f"{random.randint(-100, 100)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    MTheme().apply(demo_widget)
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
