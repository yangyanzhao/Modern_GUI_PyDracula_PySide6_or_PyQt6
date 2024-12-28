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

from PySide6 import QtWidgets

# Import third-party modules

# Import local modules
from widgets.dayu_widgets.field_mixin import MFieldMixin
from widgets.dayu_widgets.item_model import MSortFilterModel
from widgets.dayu_widgets.item_model import MTableModel
from widgets.dayu_widgets.item_view import MTreeView
from widgets.dayu_widgets.line_edit import MLineEdit
from widgets.dayu_widgets.push_button import MPushButton
from widgets.dayu_widgets.widgets_test import _mock_data


class TreeViewExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent=None):
        super(TreeViewExample, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        model_1 = MTableModel()
        model_1.set_header_list(_mock_data.header_list)
        model_1.set_data_list(_mock_data.tree_data_list)

        model_sort = MSortFilterModel()
        model_sort.setSourceModel(model_1)
        model_sort.set_header_list(_mock_data.header_list)

        tree_view = MTreeView()
        tree_view.setModel(model_sort)
        tree_view.set_header_list(_mock_data.header_list)


        line_edit = MLineEdit().search().small()
        line_edit.textChanged.connect(model_sort.set_search_pattern)

        expand_all_button = MPushButton("Expand All").small()
        expand_all_button.clicked.connect(tree_view.expandAll)
        collapse_all_button = MPushButton("Collapse All").small()
        collapse_all_button.clicked.connect(tree_view.collapseAll)
        button_lay = QtWidgets.QHBoxLayout()
        button_lay.addWidget(expand_all_button)
        button_lay.addWidget(collapse_all_button)
        button_lay.addWidget(line_edit)
        button_lay.addStretch()

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addLayout(button_lay)
        main_lay.addWidget(tree_view)
        main_lay.addStretch()
        self.setLayout(main_lay)


if __name__ == "__main__":
    # Import local modules
    from widgets.dayu_widgets import dayu_theme
    from widgets.dayu_widgets.qt import application

    with application() as app:
        test = TreeViewExample()
        dayu_theme.apply(test)
        test.show()
