#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2019.6
# Email : muyanru345@163.com
###################################################################

# Import future modules
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PySide6 import QtWidgets

# Import third-party modules

# Import local modules
from framework.widgets.dayu_widgets.divider import MDivider
from framework.widgets.dayu_widgets.push_button import MPushButton
from framework.widgets.dayu_widgets.text_edit import MTextEdit


class TextEditExample(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TextEditExample, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_lay = QtWidgets.QVBoxLayout()

        main_lay.addWidget(MDivider("no size grip"))
        main_lay.addWidget(MTextEdit(self))
        main_lay.addWidget(MDivider("size grip"))
        main_lay.addWidget(MTextEdit(self).resizeable())
        main_lay.addWidget(MPushButton("text").primary())

        self.setLayout(main_lay)


if __name__ == "__main__":
    # Import local modules
    from framework.widgets.dayu_widgets import dayu_theme
    from framework.widgets.dayu_widgets.qt import application

    with application() as app:
        test = TextEditExample()
        dayu_theme.apply(test)
        test.show()
