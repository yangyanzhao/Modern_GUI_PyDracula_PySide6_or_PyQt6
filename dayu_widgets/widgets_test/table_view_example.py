#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2019.2
# Email : muyanru345@163.com
###################################################################
# Import future modules
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import asyncio
# Import built-in modules
import functools
import sys

from PySide6 import QtWidgets, QtAsyncio
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication

# Import local modules
from dayu_widgets import dayu_theme, MTheme
from dayu_widgets.alert import MAlert
from dayu_widgets.divider import MDivider
from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.item_model import MSortFilterModel
from dayu_widgets.item_model import MTableModel
from dayu_widgets.item_view import MTableView
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.loading import MLoadingWrapper
from dayu_widgets.push_button import MPushButton
from dayu_widgets.widgets_test import _mock_data


class TableViewExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent=None):
        super(TableViewExample, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        # 构建数据模型
        model_1 = MTableModel()
        model_1.set_header_list(_mock_data.header_list)
        model_1.set_data_list(_mock_data.data_list)

        # 构建排序模型
        self.model_sort = MSortFilterModel()
        self.model_sort.setSourceModel(model_1)
        self.model_sort.set_header_list(_mock_data.header_list)

        # 构建小表格
        table_small = MTableView(size=dayu_theme.small, show_row_count=True)
        table_small.setModel(self.model_sort)
        table_small.set_header_list(_mock_data.header_list)

        # 构建带网格的表格
        table_grid = MTableView(size=dayu_theme.small, show_row_count=True)
        table_grid.setShowGrid(True)
        table_grid.setModel(self.model_sort)
        table_grid.set_header_list(_mock_data.header_list)

        # 构建大表格
        table_large = MTableView(size=dayu_theme.large, show_row_count=False)
        table_large.setModel(self.model_sort)
        table_large.set_header_list(_mock_data.header_list)

        # 构建中型表格
        self.table_default = MTableView(size=dayu_theme.medium, show_row_count=True)
        self.table_default.set_header_list(_mock_data.header_list)

        self.loading_wrapper = MLoadingWrapper(widget=self.table_default, loading=False)

        button = MPushButton(text="Get Data: 4s")
        button.clicked.connect(lambda :asyncio.ensure_future(self.get_data()))
        switch_lay = QtWidgets.QHBoxLayout()
        switch_lay.addWidget(button)
        switch_lay.addStretch()

        # 搜索栏
        line_edit = MLineEdit().search().small()
        line_edit.textChanged.connect(self.model_sort.set_search_pattern)

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(line_edit)
        main_lay.addWidget(MDivider("小型表格"))
        main_lay.addWidget(table_small)
        main_lay.addWidget(MDivider("中型表格"))
        main_lay.addLayout(switch_lay)
        main_lay.addWidget(self.loading_wrapper)
        main_lay.addWidget(MDivider("大型表格(隐藏行号)"))
        main_lay.addWidget(table_large)
        main_lay.addWidget(MDivider("网格线表格"))
        main_lay.addWidget(table_grid)
        main_lay.addStretch()
        main_lay.addWidget(MAlert('Simply use "MItemViewSet" or "MItemViewFullSet"'))
        self.setLayout(main_lay)

    async def get_data(self):
        self.loading_wrapper.set_dayu_loading(True)
        await asyncio.sleep(2)
        self.loading_wrapper.set_dayu_loading(False)
        self.table_default.setModel(self.model_sort)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = TableViewExample()
    MTheme().apply(demo_widget)
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)