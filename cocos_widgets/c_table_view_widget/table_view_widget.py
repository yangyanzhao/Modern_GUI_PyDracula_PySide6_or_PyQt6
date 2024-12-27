import asyncio
import random
import sys
from datetime import datetime
from math import ceil
from PySide6 import QtCore, QtAsyncio
from PySide6.QtCore import QModelIndex, QDateTime
from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel

from cocos_widgets.c_calendar import CCalendarWidget
from cocos_widgets.c_dialog.c_confirm_dialog import CMessageDialog, CConfirmDialog
from cocos_widgets.c_pagination_bar import CPaginationBar
from cocos_widgets.c_table_view_widget.ddl_parse_util import parse_ddl
from cocos_widgets.c_table_view_widget.icons import icons
from dayu_widgets.qt import MIcon
from dayu_widgets import MFieldMixin, dayu_theme, MTableModel, MLineEdit, \
    MTableView, MPushButtonGroup, MPushButton, MComboBox, MMenu, MFlowLayout, \
    MSpinBox, MDoubleSpinBox, MDateTimeEdit, MDateEdit, MTimeEdit, MTag
from db.mysql.async_utils import is_in_async_context

"""
增删改查窗口封装控件
"""


def is_date(date_string, date_format="%Y-%m-%d"):
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False


def is_time(time_string, time_format="%H:%M:%S"):
    try:
        datetime.strptime(time_string, time_format)
        return True
    except ValueError:
        return False


def is_datetime(datetime_string, datetime_format="%Y-%m-%d %H:%M:%S"):
    try:
        datetime.strptime(datetime_string, datetime_format)
        return True
    except ValueError:
        return False


class ColumnConfig:
    def __init__(self, label, key, default_value,
                 width=100, default_filter=False, searchable=True, editable=True,
                 selectable=False, selectable_list=None,
                 checkable=False, exclusive=True, order=None, color=None, bg_color=None, display=None, align=None,
                 font=None, icon=None,
                 tooltip=None, size=None, data=None, edit=None, draggable=None, droppable=None, op='eq'):
        self.label = label  # 必填，用来读取 model后台数据结构的属性
        self.key = key  # 必填，显示在界面的该列的名字
        self.default_value = default_value  # 必填，默认值
        self.width = width  # 选填，单元格默认的宽度
        self.default_filter = default_filter  # 选填，如果有组合的filter组件，该属性默认是否显示，默认False
        self.searchable = searchable  # 选填，如果有搜索组件，该属性是否可以被搜索，默认False
        self.editable = editable  # 选填，该列是否可以双击编辑，默认False
        self.selectable = selectable  # 选填，该列是否使用下拉列表选择。该下拉框的选项们，是通过 data 拿数据的
        self.selectable_list = selectable_list  # 选填，使用下拉列表选择,选项列表。['item1','item2']或者[{'label','启用','value':1},{'label','禁用','value':0}]
        self.checkable = checkable  # 选填，该单元格是否要加checkbox，默认False
        self.exclusive = exclusive  # 配合selectable，如果是可以多选的则为 False，如果是单选，则为True
        self.order = order  # 选填，初始化时，该列的排序方式, 0 升序，1 降序

        # 下面的是每个单元格的设置，主要用来根据本单元格数据，动态设置样式
        self.color = color  # QColor选填，该单元格文字的颜色，例如根据百分比数据大小，大于100%显示红色，小于100%显示绿色
        self.bg_color = bg_color  # 选填，该单元格的背景色，例如根据bool数据，True显示绿色，False显示红色
        self.display = display  # 选填，该单元显示的内容，例如数据是以分钟为单位，可以在这里给转换成按小时为单位
        self.align = align  # 选填，该单元格文字的对齐方式
        self.font = font  # 选填，该单元格文字的格式，例如加下划线、加粗等等
        self.icon = icon  # 选填，该单格元的图标，注意，当 QListView 使用图标模式时，每个item的图片也是在这里设置
        self.tooltip = tooltip  # 选填，鼠标指向该单元格时，显示的提示信息
        self.size = size  # 选填，该列的 hint size，设置
        self.data = data
        self.edit = edit
        self.draggable = draggable
        self.droppable = droppable
        self.op = op  # 搜索时的操作符，默认是eq，即等于，其他有ct是模糊查询，bt是区间查询，in是包含，ne是不等于，lt是小于，gt是大于，le是小于等于，ge是大于等于

    def to_dict(self):
        return {
            "label": self.label,
            "key": self.key,
            "width": self.width,
            "default_filter": self.default_filter,
            "searchable": self.searchable,
            "editable": self.editable,
            "selectable": self.selectable,
            "checkable": self.checkable,
            "exclusive": self.exclusive,
            "order": self.order,
            # 下面的是每个单元格的设置，主要用来根据本单元格数据，动态设置样式
            "color": self.color,
            "bg_color": self.bg_color,
            "display": self.display,
            "align": self.align,
            "font": self.font,
            "icon": self.icon,
            "tooltip": self.tooltip,
            "size": self.size,
            "data": self.data,
            "edit": self.edit,
            "draggable": self.draggable,
            "droppable": self.droppable,
            "op": self.op
        }


class TableViewWidgetAbstract(QWidget, MFieldMixin):
    def __init__(self, parent=None):
        super(TableViewWidgetAbstract, self).__init__(parent)

        self.parent = parent  # 父级控件
        self.page_number = 1  # 当前页码
        self.page_size = 5  # 每页数量
        self.total_count = 0  # 总数量
        self.total_page = 0  # 总页码
        self.conditions = {}  # 检索条件 格式：{field:{field:field,value:value,op:op}}
        self.orderby_list: list[tuple] = []  # 排序条件[(key1,asc),(key2,desc)]
        self.data_list = []  # 数据列表

        self.init_ui()  # 初始化UI
        self.reload_data()  # 载入数据

    # /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#
    def get_header_domain_list(self) -> list[ColumnConfig]:
        """
        获取表格配置
        """
        # header_domain_list: list[ColumnConfig] = [
        #     ColumnConfig(
        #         label="名称",
        #         key="username",
        #         default_value=""
        #     ),
        #     ColumnConfig(
        #         label="年龄",
        #         key="score",
        #         default_value=18,
        #         display=lambda x, y: f"{x}岁",
        #         color=lambda x, y: 'green' if x < 20 else 'red'
        #     )
        # ]
        # return header_domain_list
        raise NotImplementedError

    def combine_header_list(self):
        """
        预制将ID合并到表格配置
        """
        # 先判断是否有ID项，如果没有就添加
        if isinstance(self.header_list, str):
            # 这是DDL模式
            fields = parse_ddl(self.header_list)
            self.header_list = []
            for field in fields:
                field_name = field['name']
                field_type = field['type']
                field_comment = field['comment']
                self.header_list.append(ColumnConfig(label=field_comment, key=field_name))
            # print(f"配置：{self.header_list}")
        elif isinstance(self.header_list, list) and all(isinstance(item, dict) for item in self.header_list):
            # 是字典模式
            # print(f"配置：{self.header_list}")
            pass
        # 判断是否为 list[ColumnConfig]
        elif isinstance(self.header_list, list) and all(isinstance(item, ColumnConfig) for item in self.header_list):
            # 是实体模式
            self.header_list = [i.to_dict() for i in self.header_list]
            # print(f"配置：{self.header_list}")

        if "id" not in [x['key'] for x in self.header_list]:
            data = {
                "label": "ID",  # 显示名称
                "key": "id",  # 字段名称
                "checkable": True,  # 是否支持勾选
                "searchable": False,  # 是否支持搜索
                "draggable": False,  # 是否支持拖拽
                "droppable": False,  # 是否支持拖放
                "editable": False,  # 是否支持编辑(如果是下拉框，则无法双击编辑，只能下拉选择)
                "selectable": False,  # 是否支持下拉框选择，支持下拉框，需要数据中提供给key_list数据
                "exclusive": False,  # 下拉框选择是否单选
                "width": 40,  # 宽度
                # "font": lambda x, y: {"underline": True, "bold": True},  # 字体样式
                # "icon": MIcon(path=icons['新增.svg'], color='#65DB79'),  # 图标，可以动态图标
                # "display": lambda x, y: f"{x}",  # 显示格式化
                "order": QtCore.Qt.SortOrder.DescendingOrder,  # 排序
                # "bg_color": lambda x, y: "transparent" if x else dayu_theme.error_color,  # 背景颜色
                # "color": "#ff00ff",  # 文本颜色
                "op": "eq"
            }
            self.header_list.insert(0, data)
        else:
            for x in self.header_list:
                if x['key'] == 'id':
                    x['checkable'] = True

    def get_function_button(self) -> list:
        raise NotImplementedError

    def init_function_button(self):
        """
        初始化功能按钮组：新增、删除、刷新······
        """
        base_btn_list = [
            {"text": "新增", "icon": MIcon(icons['新增.svg'], "#4CAF50"), 'dayu_type': MPushButton.DefaultType,
             'clicked': self.add_btn_slot},
            {"text": "删除", "icon": MIcon(icons['删除.svg'], "#F44336"), 'dayu_type': MPushButton.DefaultType,
             'clicked': self.delete_btn_slot},
            {"text": "刷新", "icon": MIcon(icons['刷新.svg'], "#03A9F4"), 'dayu_type': MPushButton.DefaultType,
             'clicked': self.reload_data},
            {"text": "清空", "icon": MIcon(icons['清空.svg'], "#FF0000"), 'dayu_type': MPushButton.DefaultType,
             'clicked': self.truncate_btn_slot},
        ]
        if self.get_function_button() and len(self.get_function_button()) > 0:
            # 检测一下是否合规
            if not isinstance(self.get_function_button(), list):
                raise ValueError("按钮组参数不合法,必须是list")
            for btn in self.get_function_button():
                if not isinstance(btn, dict):
                    raise ValueError("按钮组配置不合法,必须是dict")
                if 'text' in btn:
                    if not isinstance(btn['text'], str):
                        raise ValueError("按钮组配置不合法,text必须是str")
                else:
                    raise ValueError("按钮组配置不合法,缺失text参数")
            base_btn_list += self.get_function_button()
        # 按钮组
        self.button_group = MPushButtonGroup()
        self.button_group.set_button_list(base_btn_list)
        self.function_button_layout = QHBoxLayout()
        self.function_button_layout.addWidget(self.button_group)
        self.function_button_layout.addStretch()

    def init_search_bar(self):
        """
        条件筛选栏初始化
        """
        self.search_bar_layout = MFlowLayout()
        self.search_bar_layout.setContentsMargins(0, 0, 0, 0)
        combo_box_list = []
        edit_list = []
        menu_list = []
        datetime_list = []
        date_list = []
        time_list = []
        for head in self.header_list:
            if 'searchable' in head and head['searchable']:
                if 'selectable' in head and head['selectable']:
                    # 下拉框
                    q_widget = QWidget()
                    layout = QHBoxLayout(q_widget)
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setSpacing(0)
                    combo_box = MComboBox().small()
                    combo_box.set_placeholder(head['label'])

                    default_data = self._get_default_data_()
                    if f"{head['key']}_list" not in default_data:
                        raise RuntimeError(f"未提供combo_box选项异常【{head['key']}_list】")
                    selections = default_data[f"{head['key']}_list"]
                    if isinstance(selections, str):
                        selections = selections.split(",")
                    menu = MMenu(parent=combo_box)
                    menu.set_data(selections)
                    combo_box.set_menu(menu)

                    def formatter_show(values, ses):
                        mapping = {}
                        for s in ses:
                            if isinstance(s, dict):
                                mapping[s['value']] = s['label']
                            else:
                                mapping[s] = s
                        if values in mapping:
                            return mapping[values]
                        return values

                    # 显示的时候要显示label而不是value
                    combo_box.set_formatter(lambda x, ses=selections: formatter_show(x, ses))

                    def changed_slot_selectable(value, h):
                        if h['key'] in self.conditions:
                            self.conditions.update(
                                {h['key']: {**self.conditions[h['key']], 'value': value, 'op': h['op']}})
                        else:
                            self.conditions.update({h['key']: {'field': h['key'], 'value': value, 'op': h['op']}})

                    combo_box.sig_value_changed.connect(lambda value, h=head: changed_slot_selectable(value, h))
                    combo_box.sig_value_changed.connect(self.reload_data)
                    if 'width' in head:
                        combo_box.setMinimumWidth(head['width'])
                    layout.addWidget(QLabel(head['label']))
                    layout.addWidget(combo_box)

                    combo_box_list.append(combo_box)  # 暂存一下，用于清理
                    menu_list.append(menu)  # 暂存一下，用于清理
                    self.search_bar_layout.addWidget(q_widget)
                else:
                    # 输入搜索
                    q_widget = QWidget()
                    layout = QHBoxLayout(q_widget)
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setSpacing(0)
                    layout.addWidget(QLabel(head['label']))
                    default_data = self._get_default_data_()
                    if f"{head['key']}" not in default_data:
                        raise RuntimeError(f"默认数据与表头配置不匹配: {head['key']}")
                    key_value = self._get_default_data_()[f"{head['key']}"]
                    # 如果是数字类型
                    if isinstance(key_value, int):
                        spin_box__small = MSpinBox().small()
                        spin_box__small.clear()

                        def changed_slot_int(value, h):
                            if h['key'] in self.conditions:
                                self.conditions.update(
                                    {h['key']: {**self.conditions[h['key']], 'value': value, 'op': h['op']}})
                            else:
                                self.conditions.update({h['key']: {'field': h['key'], 'value': value, 'op': h['op']}})

                        spin_box__small.valueChanged.connect(lambda value, h=head: changed_slot_int(value, h))
                        if 'width' in head:
                            spin_box__small.setMinimumWidth(head['width'])
                        layout.addWidget(spin_box__small)
                        edit_list.append(spin_box__small)  # 暂存一下，用于清理
                        self.search_bar_layout.addWidget(q_widget)
                    elif isinstance(key_value, float):
                        spin_box__small = MDoubleSpinBox().small()
                        spin_box__small.clear()

                        def changed_slot_float(value, h):
                            if h['key'] in self.conditions:
                                self.conditions.update(
                                    {h['key']: {**self.conditions[h['key']], 'value': value, 'op': h['op']}})
                            else:
                                self.conditions.update({h['key']: {'field': h['key'], 'value': value, 'op': h['op']}})

                        spin_box__small.valueChanged.connect(lambda value, h=head: changed_slot_float(value, h))
                        if 'width' in head:
                            spin_box__small.setMinimumWidth(head['width'])
                        layout.addWidget(spin_box__small)
                        edit_list.append(spin_box__small)  # 暂存一下，用于清理
                        self.search_bar_layout.addWidget(q_widget)
                    elif is_datetime(key_value):
                        date_time_edit_0 = MDateTimeEdit(
                            datetime=QtCore.QDateTime.fromString(key_value, "yyyy-MM-dd HH:mm:ss")).small()
                        date_time_edit_0.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
                        date_time_edit_0.setCalendarPopup(True)
                        custom_calendar = CCalendarWidget(date_time_edit_0, self)
                        layout.addWidget(custom_calendar)
                        date_time_edit_0.setCalendarWidget(custom_calendar)
                        date_time_edit_0.setDateTime(QDateTime(datetime.today().year, 1, 1, 0, 0, 0))
                        if head['op'] == 'bt':
                            def changed_slot_datetime_0(value, h):
                                if h['key'] in self.conditions:
                                    self.conditions.update(
                                        {h['key']: {**self.conditions[h['key']],
                                                    'value_0': value.toString("yyyy-MM-dd HH:mm:ss"), 'op': h['op']}})
                                else:
                                    self.conditions.update(
                                        {h['key']: {'field': h['key'], 'value_0': value.toString("yyyy-MM-dd HH:mm:ss"),
                                                    'op': h['op']}})

                            date_time_edit_0.dateTimeChanged.connect(
                                lambda value, h=head: changed_slot_datetime_0(value, h))
                        else:
                            def changed_slot_datetime(value, h):
                                if h['key'] in self.conditions:
                                    self.conditions.update(
                                        {h['key']: {**self.conditions[h['key']],
                                                    'value': value.toString("yyyy-MM-dd HH:mm:ss"), 'op': h['op']}})
                                else:
                                    self.conditions.update(
                                        {h['key']: {'field': h['key'], 'value': value.toString("yyyy-MM-dd HH:mm:ss"),
                                                    'op': h['op']}})

                            date_time_edit_0.dateTimeChanged.connect(
                                lambda value, h=head: changed_slot_datetime(value, h))

                        layout.addWidget(date_time_edit_0)
                        datetime_list.append(date_time_edit_0)  # 暂存一下，用于清理
                        if head['op'] == 'bt':
                            date_time_edit_1 = MDateTimeEdit(
                                datetime=QtCore.QDateTime.fromString(key_value, "yyyy-MM-dd HH:mm:ss")).small()
                            date_time_edit_1.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
                            date_time_edit_1.setCalendarPopup(True)
                            custom_calendar = CCalendarWidget(date_time_edit_0, self)
                            layout.addWidget(custom_calendar)
                            date_time_edit_1.setCalendarWidget(custom_calendar)
                            date_time_edit_1.setDateTime(QDateTime(datetime.today().year, 1, 1, 0, 0, 0))

                            def changed_slot_datetime_1(value, h):
                                if h['key'] in self.conditions:
                                    self.conditions.update(
                                        {h['key']: {**self.conditions[h['key']],
                                                    'value_1': value.toString("yyyy-MM-dd HH:mm:ss"), 'op': h['op']}})
                                else:
                                    self.conditions.update(
                                        {h['key']: {'field': h['key'], 'value_1': value.toString("yyyy-MM-dd HH:mm:ss"),
                                                    'op': h['op']}})

                            date_time_edit_1.dateTimeChanged.connect(
                                lambda value, h=head: changed_slot_datetime_1(value, h))

                            layout.addWidget(date_time_edit_1)
                            datetime_list.append(date_time_edit_1)  # 暂存一下，用于清理
                        self.search_bar_layout.addWidget(q_widget)
                    elif is_date(key_value):
                        date_edit_0 = MDateEdit().small()
                        date_edit_0.setDisplayFormat("yyyy-MM-dd")
                        date_edit_0.setCalendarPopup(True)
                        custom_calendar = CCalendarWidget(date_edit_0, self)
                        layout.addWidget(custom_calendar)
                        date_edit_0.setCalendarWidget(custom_calendar)
                        date_edit_0.setDateTime(QDateTime(100, 1, 1, 0, 0, 0))
                        date_edit_0.setSpecialValueText("选择日期")
                        if head['op'] == 'bt':
                            def changed_slot_date_0(value, h):
                                if h['key'] in self.conditions:
                                    self.conditions.update(
                                        {h['key']: {**self.conditions[h['key']],
                                                    'value_0': value.toString("yyyy-MM-dd"), 'op': h['op']}})
                                else:
                                    self.conditions.update(
                                        {h['key']: {'field': h['key'], 'value_0': value.toString("yyyy-MM-dd"),
                                                    'op': h['op']}})

                            date_edit_0.dateChanged.connect(lambda value, h=head: changed_slot_date_0(value, h))
                        else:
                            def changed_slot_date(value, h):
                                if h['key'] in self.conditions:
                                    self.conditions.update(
                                        {h['key']: {**self.conditions[h['key']], 'value': value.toString("yyyy-MM-dd"),
                                                    'op': h['op']}})
                                else:
                                    self.conditions.update(
                                        {h['key']: {'field': h['key'], 'value': value.toString("yyyy-MM-dd"),
                                                    'op': h['op']}})
                                pass

                            date_edit_0.dateChanged.connect(lambda value, h=head: changed_slot_date(value, h))

                        layout.addWidget(date_edit_0)
                        date_list.append(date_edit_0)  # 暂存一下，用于清理
                        if head['op'] == 'bt':
                            date_edit_1 = MDateEdit(
                                date=QtCore.QDate.fromString(key_value, "yyyy-MM-dd")).small()
                            date_edit_1.setDisplayFormat("yyyy-MM-dd")
                            date_edit_1.setCalendarPopup(True)
                            custom_calendar = CCalendarWidget(date_edit_1, self)
                            layout.addWidget(custom_calendar)
                            date_edit_1.setCalendarWidget(custom_calendar)
                            date_edit_1.setDateTime(QDateTime(100, 1, 1, 0, 0, 0))
                            date_edit_1.setSpecialValueText("选择日期")

                            def changed_slot_date_1(value, h):
                                if h['key'] in self.conditions:
                                    self.conditions.update(
                                        {h['key']: {**self.conditions[h['key']],
                                                    'value_1': value.toString("yyyy-MM-dd"), 'op': h['op']}})
                                else:
                                    self.conditions.update(
                                        {h['key']: {'field': h['key'], 'value_1': value.toString("yyyy-MM-dd"),
                                                    'op': h['op']}})

                            date_edit_1.dateChanged.connect(lambda value, h=head: changed_slot_date_1(value, h))
                            layout.addWidget(date_edit_1)
                            date_list.append(date_edit_1)  # 暂存一下，用于清理
                        self.search_bar_layout.addWidget(q_widget)
                    elif is_time(key_value):
                        time_edit_0 = MTimeEdit().small()
                        time_edit_0.setDisplayFormat("HH:mm:ss")
                        time_edit_0.setDateTime(QDateTime(100, 1, 1, 0, 0, 0))
                        time_edit_0.setSpecialValueText("选择时间")
                        if head['op'] == 'bt':
                            def changed_slot_time_0(value, h):
                                if h['key'] in self.conditions:
                                    self.conditions.update(
                                        {h['key']: {**self.conditions[h['key']], 'value_0': value.toString("HH:mm:ss"),
                                                    'op': h['op']}})
                                else:
                                    self.conditions.update(
                                        {h['key']: {'field': h['key'], 'value_0': value.toString("HH:mm:ss"),
                                                    'op': h['op']}})

                            time_edit_0.timeChanged.connect(lambda value, h=head: changed_slot_time_0(value, h))
                        else:
                            def changed_slot_time(value, h):
                                if h['key'] in self.conditions:
                                    self.conditions.update(
                                        {h['key']: {**self.conditions[h['key']], 'value': value.toString("HH:mm:ss"),
                                                    'op': h['op']}})
                                else:
                                    self.conditions.update(
                                        {h['key']: {'field': h['key'], 'value': value.toString("HH:mm:ss"),
                                                    'op': h['op']}})

                            time_edit_0.timeChanged.connect(lambda value, h=head: changed_slot_time(value, h))

                        layout.addWidget(time_edit_0)
                        time_list.append(time_edit_0)  # 暂存一下，用于清理
                        if head['op'] == 'bt':
                            time_edit_1 = MTimeEdit(
                                time=QtCore.QTime.fromString(key_value, "HH:mm:ss")).small()
                            time_edit_1.setDisplayFormat("HH:mm:ss")
                            time_edit_1.setCalendarPopup(True)
                            time_edit_0.setDateTime(QDateTime(100, 1, 1, 0, 0, 0))
                            time_edit_0.setSpecialValueText("选择时间")

                            def changed_slot_time_1(value, h):
                                if h['key'] in self.conditions:
                                    self.conditions.update(
                                        {h['key']: {**self.conditions[h['key']], 'value_1': value.toString("HH:mm:ss"),
                                                    'op': h['op']}})
                                else:
                                    self.conditions.update(
                                        {h['key']: {'field': h['key'], 'value_1': value.toString("HH:mm:ss"),
                                                    'op': h['op']}})

                            time_edit_1.timeChanged.connect(lambda value, h=head: changed_slot_time_1(value, h))
                            layout.addWidget(time_edit_1)
                            time_list.append(time_edit_1)  # 暂存一下，用于清理
                        self.search_bar_layout.addWidget(q_widget)
                    else:
                        # 输入框兜底
                        edit__small = MLineEdit().small()
                        edit__small.set_delay_duration(2000)

                        def changed_slot_(value, h):
                            if h['key'] in self.conditions:
                                self.conditions.update(
                                    {h['key']: {**self.conditions[h['key']], 'value': value, 'op': h['op']}})
                            else:
                                self.conditions.update({h['key']: {'field': h['key'], 'value': value, 'op': h['op']}})

                        edit__small.textChanged.connect(lambda value, h=head: changed_slot_(value, h))
                        edit__small.returnPressed.connect(self.reload_data)
                        if 'width' in head:
                            edit__small.setMinimumWidth(head['width'])
                        layout.addWidget(edit__small)
                        edit_list.append(edit__small)  # 暂存一下，用于清理
                        self.search_bar_layout.addWidget(q_widget)
        search_btn = MPushButton("搜索").primary().small()
        search_btn.clicked.connect(self.reload_data)
        self.search_bar_layout.addWidget(search_btn)
        reset_btn = MPushButton("重置").small()

        self.order_list_widget = QWidget()
        self.order_list_flow_layout = MFlowLayout(self.order_list_widget)

        def reset_slot():
            self.conditions.clear()
            for combo_box in combo_box_list:
                combo_box.setCurrentIndex(-1)
            for edit in edit_list:
                edit.clear()
            for menu in menu_list:
                for action in menu.actions():
                    action.setChecked(False)
                    action.setChecked(False)  # 对于可以选中的菜单项
                    action.setChecked(False)  # 对于可以选中的菜单项
            for datetime in datetime_list:
                datetime.setDateTime(QDateTime(100, 1, 1, 0, 0, 0))
                datetime.setSpecialValueText("选择日期日期")
            for date in date_list:
                date.setDateTime(QDateTime(100, 1, 1, 0, 0, 0))
                date.setSpecialValueText("选择日期")
            for time in time_list:
                time.setDateTime(QDateTime(100, 1, 1, 0, 0, 0))
                time.setSpecialValueText("选择时间")
            pass
            self.orderby_list.clear()
            self.reload_orderby()
            self.conditions.clear()
            self.reload_data()

        reset_btn.clicked.connect(reset_slot)
        self.search_bar_layout.addWidget(reset_btn)

    def reload_orderby(self):
        self.order_list_widget.show()
        # 清空布局中的所有控件
        while self.order_list_flow_layout.count():
            item = self.order_list_flow_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        if len(self.orderby_list) == 0:
            self.order_list_widget.hide()
        for key, order in self.orderby_list:
            hex_color = f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"
            display_key = key
            if order == 'asc':
                display_key += " ↑↑        "
            if order == 'desc':
                display_key += " ↓↓        "
            tag = MTag(display_key).no_border().coloring(hex_color).closeable()
            tag.sig_closed.connect(lambda k=key, o=order: (self.orderby_list.remove((k, o)), self.reload_orderby()))
            self.order_list_flow_layout.addWidget(tag)

    def init_table_view(self):
        """
        初始化表格
        """
        self.table_widget = QWidget()
        layout = QVBoxLayout(self.table_widget)
        self.combine_header_list()
        # 构建数据模型
        self.table_model = MTableModel()

        self.table_model.set_header_list(self.header_list)
        # 修改数据
        self.table_model.dataChanged.connect(self.data_changed_slot)

        # 构建表格
        self.table_view = MTableView(size=dayu_theme.small, show_row_count=False)

        def sort_by_head(head_index):
            key = self.header_list[head_index]['key']
            if (key, 'asc') in self.orderby_list:
                # 如果是正序，则反序
                self.orderby_list.remove((key, 'asc'))
                self.orderby_list.insert(0, (key, 'desc'))
            elif (key, 'desc') in self.orderby_list:
                # 如果已经是反序，则删掉
                self.orderby_list.remove((key, 'desc'))
            else:
                # 第一次则添加一个顺序的
                self.orderby_list.insert(0, (key, 'asc'))
            self.reload_orderby()
            self.reload_data()

        self.table_view.horizontalHeader().sectionClicked.connect(sort_by_head)  # 点击表头排序
        self.table_view.setModel(self.table_model)
        self.table_view.set_header_list(self.header_list)
        self.table_view.setShowGrid(True)
        self.table_view.enable_context_menu(True)
        layout.addWidget(self.table_view)
        # 分页控件
        self.paginationBar = CPaginationBar(self, totalPages=20)
        self.paginationBar.setInfos(f'共 {self.total_count} 条')
        self.paginationBar.pageChanged.connect(self.page_changed_slot)

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.header_domain_list = self.get_header_domain_list()  # 表格配置实体
        self.header_list = [i.to_dict() for i in self.get_header_domain_list()]  # 表格配置字典
        self.init_function_button()  # 初始化功能组
        self.init_table_view()  # 初始化表格
        self.init_search_bar()  # 初始化条件筛选

        # 排版
        self.layout.addLayout(self.function_button_layout)  # 功能组
        self.layout.addLayout(self.search_bar_layout)  # 检索栏
        self.layout.addWidget(self.order_list_widget)  # 排序栏
        self.layout.addWidget(self.table_view)  # 动画 + 表格
        self.layout.addWidget(self.paginationBar)  # 分页卡片
        self.layout.addStretch()

    # /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#
    def reload_data(self, *args, **kwargs):
        """
        加载数据,后台查询数据后，载入model
        :return:
        """

        def handle_data_list(total_count, data_list):
            self.total_count = total_count
            self.data_list = data_list
            # 要对data_list进行处理，field_list数据是字符串，要转成列表才行。
            selectable_keys = [i['key'] for i in self.header_list if 'selectable' in i and i['selectable']]
            for data in self.data_list:
                for selectable_key in selectable_keys:
                    if f'{selectable_key}_list' in data:
                        if isinstance(data[f'{selectable_key}_list'], str):
                            data[f'{selectable_key}_list'] = data[f'{selectable_key}_list'].split(',')
            # 载入表格
            self.table_model.set_data_list(self.data_list)
            self.total_page = ceil(self.total_count / self.page_size)  # 计算总页码
            self.paginationBar.setTotalPages(self.total_page)
            self.paginationBar.setInfos(f'共 {self.total_count} 条')
            self.paginationBar.setCurrentPage(self.page_number)

        self.total_page = ceil(self.total_count / self.page_size)  # 计算总页码
        # 防止超页
        if self.page_number > self.total_page and self.page_number != 1:
            self.page_number = self.total_page
        if is_in_async_context():
            loop = asyncio.get_event_loop()
            running = loop.is_running()
            if running:
                def callback(t):
                    count, datas = t.result()
                    handle_data_list(count, datas)

                task = asyncio.create_task(
                    self.select_api(self.page_number, self.page_size, self.conditions, self.orderby_list))
                task.add_done_callback(callback)
        else:
            total_count, data_list = asyncio.run(
                self.select_api(self.page_number, self.page_size, self.conditions, self.orderby_list))
            handle_data_list(total_count, data_list)

    # /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#
    def page_changed_slot(self, page):
        """
        切换页码
        :param page:
        :return:
        """
        self.page_number = page
        self.reload_data()

    def data_changed_slot(self, param: QModelIndex):
        """
        编辑数据
        :param param:
        :return:
        """
        row = param.row()  # 行号
        column = param.column()  # 列号
        if param.isValid():
            model: MTableModel = param.model()  # 数据模型
            row_data = model.get_data_list()[row]  # 当前行数据，xxx_checked是否选中
            copy = row_data.copy()
            del copy['_parent']  # 去除出循环引用
            if is_in_async_context():
                if asyncio.get_event_loop().is_running():
                    task = asyncio.create_task(self.update_api(data=copy, id=copy['id']))
                    task.add_done_callback(lambda t: self.reload_data())
                    asyncio.gather(task)
                else:
                    pass
            else:
                pass
            # self.reload_data() # 这里重新加载数据没有意义，因此此时异步任务还没有完成。

    def add_btn_slot(self):
        """
        新增数据
        :return:
        """
        if is_in_async_context():
            if asyncio.get_event_loop().is_running():
                task = asyncio.create_task(self.insert_api())
                task.add_done_callback(lambda t: self.reload_data())
                asyncio.gather(task)
            else:
                pass
        else:
            pass
        self.total_count += + 1
        self.total_page = ceil(self.total_count / self.page_size)
        self.page_number = self.total_page
        self.paginationBar.setCurrentPage(self.page_number)
        CMessageDialog.success(content="新增成功", parent=self, is_mask=False)

    def delete_btn_slot(self):
        """
        删除数据
        :return:
        """
        data_list = self.table_model.get_data_list()
        # 删除选中项
        checked_doc_ids = []
        for data in data_list:
            if data.get("id_checked", 0) is not None and isinstance(data.get("id_checked", 0), int):
                if data.get("id_checked", 0) == 2:
                    checked_doc_ids.append(data['id'])
            else:
                if data.get("id_checked", 0) is not None and data.get("id_checked", 0).value == 2:
                    checked_doc_ids.append(data['id'])
        if len(checked_doc_ids) == 0:
            CMessageDialog.error("Please select the data first.", parent=self)
            return

        confirm = CConfirmDialog.warning(title="删除",
                                         content="您确定要删除吗？",
                                         parent=self)
        exec_ = confirm.exec_()
        if exec_ == 1:
            if is_in_async_context():
                if asyncio.get_event_loop().is_running():
                    task = asyncio.create_task(self.delete_api(checked_doc_ids))
                    task.add_done_callback(lambda t: self.reload_data())
                else:
                    pass
            else:
                pass
            self.total_count = self.total_count - len(set(checked_doc_ids))
            # self.reload_data() # 这里重新加载数据没有意义，因此此时异步任务还没有完成。
            CMessageDialog.success(content="删除成功", parent=self, is_mask=False)
        else:
            return

    def truncate_btn_slot(self):
        """
        截断数据（清空数据表）
        :return:
        """

        confirm = CConfirmDialog.danger(title="清空",
                                        content="您确定要清空吗？",
                                        parent=self)
        exec_ = confirm.exec_()
        if exec_ == 1:
            if is_in_async_context():
                if asyncio.get_event_loop().is_running():
                    task = asyncio.create_task(self.truncate_api())
                    task.add_done_callback(lambda t: self.reload_data())
                    asyncio.gather(task)
                else:
                    pass
            else:
                pass

            # self.reload_data() # 这里重新加载数据没有意义，因此此时异步任务还没有完成。去异步任务完成时回调的时候加载
            CMessageDialog.success(content="清空成功", parent=self, is_mask=False)
        else:
            return

    # /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

    async def update_api(self, data, id) -> bool:
        """
        JDBC 更新API 这里根据不同的数据库类型，执行不同的更新语句
        :param data 数据内容
        :param id 数据ID
        """
        raise NotImplementedError

    async def delete_api(self, id_list: list) -> bool:
        """
        JDBC 删除API 这里根据不同的数据库类型，执行不同的删除语句
        :param id_list id列表
        """
        raise NotImplementedError

    async def insert_api(self, data=None) -> bool:
        """
        JDBC 新增API 这里根据不同的数据库类型，执行不同的新增语句
        """
        # 获取默认数据，进行插入数据库，然后用户通过修改去填入数据
        raise NotImplementedError

    async def select_api(self, page_number, page_size, conditions: dict = None, orderby_list=None) -> (int, list[dict]):
        """
        JDBC 查询API 这里根据不同的数据库类型，执行不同的查询语句
        :param page_number: 页码
        :param page_size: 每页数量
        :param conditions: 条件字典，格式：{field:{field:field,value:value,op:op}}。field为字段名，value为条件值，op为查询方式【op为模糊，eq为精确查询，bt为范围查询（value_0,value_1）,in为包含查询（values:list）......】：[{'field':'command','value':'ASBC','op':'ct'}]
        :param orderby_list: 排序列表,field为字段名，value为排序值【'asc','desc'】：[{'field':'command','value':'asc'}]
        :return: (总数量, 数据列表)数据列表必须字典类型的列表，且必须带有id字段（删除是根据id来删除）
        """

        raise NotImplementedError

    async def truncate_api(self):
        raise NotImplementedError

    def _get_default_data_(self):
        """
        提取默认数据
        """
        # 处理一下head_domain_list,提取出默认数据
        header_domain_list = self.get_header_domain_list()
        default_data = {}
        for header_domain in header_domain_list:
            default_data[header_domain.key] = header_domain.default_value
            if header_domain.selectable:
                if header_domain.selectable_list is None:
                    raise ValueError(f"{header_domain.key} selectable_list is None.")
                default_data[f'{header_domain.key}_list'] = header_domain.selectable_list
        return default_data
