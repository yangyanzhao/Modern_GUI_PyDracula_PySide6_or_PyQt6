#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2019.2
# Email : muyanru345@163.com
###################################################################
"""
Example code for MDateTimeEdit, MDoubleSpinBox, MSpinBox, MTimeEdit, MDateEdit
"""
# Import future modules
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PySide6 import QtWidgets

# Import local modules
from framework.widgets.dayu_widgets.divider import MDivider
from framework.widgets.dayu_widgets.spin_box import MDateEdit
from framework.widgets.dayu_widgets.spin_box import MDateTimeEdit
from framework.widgets.dayu_widgets.spin_box import MDoubleSpinBox
from framework.widgets.dayu_widgets.spin_box import MSpinBox
from framework.widgets.dayu_widgets.spin_box import MTimeEdit


class SpinBoxExample(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SpinBoxExample, self).__init__(parent)
        self.setWindowTitle("Examples for Spin Box")

        main_lay = QtWidgets.QVBoxLayout()
        class_list = [MSpinBox, MDoubleSpinBox, MDateTimeEdit, MDateEdit, MTimeEdit]
        for cls in class_list:
            main_lay.addWidget(MDivider(cls.__name__))
            lay = QtWidgets.QHBoxLayout()
            lay.addWidget(cls().large())
            lay.addWidget(cls().medium())
            lay.addWidget(cls().small())
            main_lay.addLayout(lay)

        main_lay.addWidget(MDivider("Pop Calendar Widget"))
        date_time_edit = MDateTimeEdit()
        date_time_edit.setCalendarPopup(True)
        date_edit = MDateEdit()
        date_edit.setCalendarPopup(True)
        time_edit = MTimeEdit()
        time_edit.setCalendarPopup(True)
        date_lay = QtWidgets.QHBoxLayout()
        date_lay.addWidget(date_time_edit)
        date_lay.addWidget(date_edit)
        date_lay.addWidget(time_edit)
        main_lay.addLayout(date_lay)

        main_lay.addStretch()
        self.setLayout(main_lay)


if __name__ == "__main__":
    # Import local modules
    from framework.widgets.dayu_widgets import dayu_theme
    from framework.widgets.dayu_widgets.qt import application

    with application() as app:
        test = SpinBoxExample()
        dayu_theme.apply(test)
        test.show()
