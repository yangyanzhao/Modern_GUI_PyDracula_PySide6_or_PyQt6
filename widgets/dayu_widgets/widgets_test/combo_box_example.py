import random

from PySide6 import QtWidgets
from widgets.dayu_widgets import MFieldMixin


class ComboBoxExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent=None):
        super(ComboBoxExample, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        cities = ["北京", "上海", "广州", "深圳"]
        self.register_field("button1_selected", "北京")
        menu1 = MMenu(parent=self)
        menu1.set_data(cities)
        size_list = [
            ("Large", dayu_theme.large),
            ("Medium", dayu_theme.medium),
            ("Small", dayu_theme.small),
        ]
        size_lay = QtWidgets.QHBoxLayout()
        for label, size in size_list:
            combo_box = MComboBox()
            combo_box.set_dayu_size(size)
            combo_box.set_menu(menu1)
            size_lay.addWidget(combo_box)
            self.bind(
                "button1_selected", combo_box, "value", signal="sig_value_changed"
            )

        self.register_field("button2_selected", ["北京"])
        menu2 = MMenu(exclusive=False, parent=self)
        menu2.set_data(cities)
        select2 = MComboBox()
        select2.set_menu(menu2)
        self.bind("button2_selected", select2, "value", signal="sig_value_changed")

        def dynamic_get_city():
            data = cities + ["郑州", "石家庄"]
            start = random.randint(0, len(data))
            end = random.randint(start, len(data))
            return data[start:end]

        self.register_field("button3_selected", "")
        menu3 = MMenu(parent=self)
        menu3.set_load_callback(dynamic_get_city)
        select3 = MComboBox()
        select3.set_menu(menu3)
        self.bind("button3_selected", select3, "value", signal="sig_value_changed")

        a = [
            {
                "children": [{"value": "Gugong", "label": "故宫"}, {"value": "Tiantan", "label": "天坛"},
                             {"value": "Wangfujing", "label": "王府井"}],
                "value": "Beijing",
                "label": "北京",
            },
            {
                "children": [{"value": "Gugong", "label": "故宫"}],
                "value": "Dongjing",
                "label": "东京",
            },
            {
                "children": [
                    {
                        "children": [{"value": "Fuzimiao", "label": "夫子庙"}],
                        "value": "Nanjing",
                        "label": "南京",
                    },
                    {
                        "children": [{"value": "Zhuozhengyuan", "label": "拙政园"},
                                     {"value": "Shizilin", "label": "狮子林"}],
                        "value": "Suzhou",
                        "label": "苏州",
                    },
                ],
                "value": "Jiangsu",
                "label": "江苏",
            },
        ]

        self.register_field("button4_selected", "")

        menu4 = MMenu(cascader=True, parent=self)
        menu4.set_data(a)
        select4 = MComboBox()
        select4.set_menu(menu4)

        def formatter_show(values):
            # 这里应该将value转换成label来显示
            # 递归函数，用于查找匹配的label
            pass

            def find_label(data, value):
                for item in data:
                    if item["value"] == value:
                        return item["label"]
                    if "children" in item:
                        result = find_label(item["children"], value)
                        if result:
                            return result
                return None

            if isinstance(values, list):
                # 转换b中的value为label
                labels = [find_label(a, value) for value in values]
                if None in labels:
                    return values
                return " / ".join(labels)
            if isinstance(values, str):
                return values

        select4.set_formatter(formatter_show)

        self.bind("button4_selected", select4, "value", signal="sig_value_changed")
        select4.set_value("北京/故宫")

        self.register_field("button5_selected", "")
        menu5 = MMenu(exclusive=False, parent=self)
        menu5.set_data(cities)
        select5 = MComboBox()
        select5.set_menu(menu5)
        select5.set_formatter(lambda x: " & ".join(x))
        self.bind("button5_selected", select5, "value", signal="sig_value_changed")

        sub_lay1 = QtWidgets.QHBoxLayout()
        sub_lay1.addWidget(MLabel("普通单选各种尺寸"))
        sub_lay1.addLayout(size_lay)
        sub_lay1.addStretch()
        sub_lay2 = QtWidgets.QHBoxLayout()
        sub_lay2.addWidget(MLabel("多选"))
        sub_lay2.addWidget(select2)
        sub_lay2.addStretch()
        sub_lay3 = QtWidgets.QHBoxLayout()
        sub_lay3.addWidget(MLabel("动态生成选项"))
        sub_lay3.addWidget(select3)
        sub_lay3.addStretch()
        sub_lay4 = QtWidgets.QHBoxLayout()
        sub_lay4.addWidget(MLabel("级联选择"))
        sub_lay4.addWidget(select4)
        sub_lay4.addStretch()
        sub_lay5 = QtWidgets.QHBoxLayout()
        sub_lay5.addWidget(MLabel("自定义显示"))
        sub_lay5.addWidget(select5)
        sub_lay5.addStretch()

        sub_lay6 = QtWidgets.QHBoxLayout()
        combo = MComboBox()
        items = cities + ["北戴河"]

        items += ["a" * i for i in range(20)]
        combo.addItems(items)
        combo.setProperty("searchable", True)
        sub_lay6.addWidget(MLabel("搜索补全"))
        sub_lay6.addWidget(combo)

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("Select"))
        main_lay.addLayout(sub_lay1)
        main_lay.addLayout(sub_lay2)
        main_lay.addLayout(sub_lay3)
        main_lay.addWidget(MDivider("自定义格式"))
        main_lay.addLayout(sub_lay4)
        main_lay.addLayout(sub_lay5)
        main_lay.addLayout(sub_lay6)
        main_lay.addStretch()

        self.setLayout(main_lay)


if __name__ == "__main__":
    # Import local modules
    from widgets.dayu_widgets import dayu_theme, MFieldMixin, MMenu, MComboBox, MDivider, MLabel
    from widgets.dayu_widgets.qt import application

    with application() as app:
        test = ComboBoxExample()
        dayu_theme.apply(test)
        test.show()
