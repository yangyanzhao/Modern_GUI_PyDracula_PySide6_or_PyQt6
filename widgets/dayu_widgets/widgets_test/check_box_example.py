import functools
import random
import sys

from PySide6 import QtAsyncio
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from widgets.dayu_widgets.qt import MIcon
from widgets.dayu_widgets import MTheme, MCheckBoxGroup, MPushButton, MFieldMixin, MCheckableTag


class DemoWidget(QWidget, MFieldMixin):
    def __init__(self, parent=None):
        super(DemoWidget, self).__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        # 组
        check_box_group = MCheckBoxGroup()
        self.app_data = [
            {"text": "Maya", "icon": MIcon("app-maya.png")},
            {"text": "Nuke", "icon": MIcon("app-nuke.png")},
            {"text": "Houdini", "icon": MIcon("app-houdini.png")},
        ]
        check_box_group.set_button_list(self.app_data)
        data_dict = {"text": "Photoshop", "icon": MIcon("app-photoshop.png")}
        check_box_group.add_button(data_dict=data_dict)
        check_box_group.set_dayu_checked(["Nuke", "Photoshop"])
        layout.addWidget(check_box_group)
        check_box_group.sig_checked_changed.connect(lambda: print("变哈"))
        self.data_list = ["北京", "上海", "广州", "深圳", "郑州", "石家庄"]
        radio_group_b = MCheckBoxGroup()
        # 设置选项
        radio_group_b.set_button_list(self.data_list)
        # 注册数据属性
        self.register_field("checked_list", ["北京", "郑州"])  # 已选中的数据
        # 进行双向绑定
        self.bind(data_name="checked_list", widget=radio_group_b, qt_property="dayu_checked", signal="sig_checked_changed")
        button = MPushButton(text="Change Value")
        button.clicked.connect(functools.partial(lambda: self.set_field("checked_list", self.data_list[random.randint(0, len(self.data_list)):len(self.data_list)])))
        layout.addWidget(radio_group_b)
        layout.addWidget(button)
        # 自定义全选、取消全选、反选
        button_all = MPushButton(text="全选")
        button_none = MPushButton(text="取消")
        button_invert = MPushButton(text="反选")
        button_all.clicked.connect(functools.partial(check_box_group._slot_set_select, True))
        button_none.clicked.connect(functools.partial(check_box_group._slot_set_select, False))
        button_invert.clicked.connect(functools.partial(check_box_group._slot_set_select, None))
        layout.addWidget(button_all)
        layout.addWidget(button_none)
        layout.addWidget(button_invert)
        layout.addWidget(MCheckableTag(text="测试"))
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    MTheme().apply(demo_widget)
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
