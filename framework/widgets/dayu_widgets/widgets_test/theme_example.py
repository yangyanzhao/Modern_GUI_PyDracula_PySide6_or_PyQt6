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

from PySide6 import QtWidgets, QtCore

# Import third-party modules

# Import local modules
from framework.widgets.dayu_widgets.button_group import MRadioButtonGroup
from framework.widgets.dayu_widgets.check_box import MCheckBox
from framework.widgets.dayu_widgets.combo_box import MComboBox
from framework.widgets.dayu_widgets.divider import MDivider
from framework.widgets.dayu_widgets.field_mixin import MFieldMixin
from framework.widgets.dayu_widgets.line_edit import MLineEdit
from framework.widgets.dayu_widgets.push_button import MPushButton
from framework.widgets.dayu_widgets.qt import MIcon
from framework.widgets.dayu_widgets.slider import MSlider
from framework.widgets.dayu_widgets.spin_box import MDateEdit
from framework.widgets.dayu_widgets.spin_box import MSpinBox
from framework.widgets.dayu_widgets.switch import MSwitch


class ThemeExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent=None):
        super(ThemeExample, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        form_lay = QtWidgets.QFormLayout()
        form_lay.setLabelAlignment(QtCore.Qt.AlignRight)
        gender_grp = MRadioButtonGroup()
        gender_grp.set_button_list(
            [
                {"text": "Female", "icon": MIcon("female.svg")},
                {"text": "Male", "icon": MIcon("male.svg")},
            ]
        )

        country_combo_box = MComboBox().small()
        country_combo_box.addItems(["China", "France", "Japan", "US"])
        date_edit = MDateEdit().small()
        date_edit.setCalendarPopup(True)

        form_lay.addRow("Name:", MLineEdit().small())
        form_lay.addRow("Gender:", gender_grp)
        form_lay.addRow("Age:", MSpinBox().small())
        form_lay.addRow("Password:", MLineEdit().small().password())
        form_lay.addRow("Country:", country_combo_box)
        form_lay.addRow("Birthday:", date_edit)
        switch = MSwitch()
        switch.setChecked(True)
        form_lay.addRow("Switch:", switch)
        slider = MSlider()
        slider.setValue(30)
        form_lay.addRow("Slider:", slider)

        button_lay = QtWidgets.QHBoxLayout()
        button_lay.addStretch()
        button_lay.addWidget(MPushButton(text="Submit").primary())
        button_lay.addWidget(MPushButton(text="Cancel"))

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addLayout(form_lay)
        main_lay.addWidget(MCheckBox("I accept the terms and conditions"))
        main_lay.addStretch()
        main_lay.addWidget(MDivider())
        main_lay.addLayout(button_lay)
        self.setLayout(main_lay)


if __name__ == "__main__":
    # Import local modules
    from framework.widgets.dayu_widgets import dayu_theme
    from framework.widgets.dayu_widgets.qt import application

    with application() as app:
        test = ThemeExample()
        dayu_theme.apply(test)
        test.show()
