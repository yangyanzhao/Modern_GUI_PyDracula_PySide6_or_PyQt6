#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2019.8
# Email : muyanru345@163.com
###################################################################
"""
MNewTag
"""
from PySide6.QtCore import Signal, Qt, QEvent
from PySide6.QtWidgets import QWidget, QGridLayout

# Import third-party modules
from framework.widgets.dayu_widgets import dayu_theme
from framework.widgets.dayu_widgets import utils
from framework.widgets.dayu_widgets.line_edit import MLineEdit
from framework.widgets.dayu_widgets.mixin import cursor_mixin
from framework.widgets.dayu_widgets.qt import get_scale_factor
from framework.widgets.dayu_widgets.theme import QssTemplate
from framework.widgets.dayu_widgets.tool_button import MToolButton



@cursor_mixin
class MNewTag(QWidget):
    """New Tag input component."""

    sig_add_tag = Signal(str)

    def __init__(self, text="New Tag", parent=None):
        super(MNewTag, self).__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground)
        self._add_button = MToolButton().text_beside_icon().small().svg("add_line.svg")
        self._add_button.setText(text)
        self._add_button.clicked.connect(self._slot_show_edit)
        self._line_edit = MLineEdit().small()
        self._line_edit.returnPressed.connect(self._slot_return_pressed)
        self._line_edit.setVisible(False)
        self._line_edit.installEventFilter(self)

        self._main_lay = QGridLayout()
        self._main_lay.setContentsMargins(3, 3, 3, 3)
        self._main_lay.addWidget(self._add_button, 0, 0)
        self._main_lay.addWidget(self._line_edit, 0, 0)
        self.setLayout(self._main_lay)
        scale_x, _ = get_scale_factor()
        style = QssTemplate(
            """
            MNewTag{
                border: @border@unit dashed @border_color;
            }
            MNewTag MToolButton:hover{
                border:none;
            }
            """
        )
        self.setStyleSheet(
            style.substitute(
                border_color=utils.fade_color(dayu_theme.secondary_text_color, "35%"),
                unit=dayu_theme.unit,
                border=1 * scale_x,
            )
        )

    def set_completer(self, completer):
        """Set the input completer"""
        self._line_edit.setCompleter(completer)

    def _slot_show_edit(self):
        self._line_edit.setVisible(True)
        self._add_button.setVisible(False)
        self._line_edit.setFocus(Qt.MouseFocusReason)

    def _slot_return_pressed(self):
        self._line_edit.setVisible(False)
        self._add_button.setVisible(True)
        if self._line_edit.text():
            self.sig_add_tag.emit(self._line_edit.text())
        self._line_edit.clear()
        self.update()

    def focusOutEvent(self, *args, **kwargs):
        """Override focusOutEvent to change the edit mode to button mode."""
        self._line_edit.setVisible(False)
        self._add_button.setVisible(True)
        return super(MNewTag, self).focusOutEvent(*args, **kwargs)

    def eventFilter(self, widget, event):
        if widget is self._line_edit:
            if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key_Escape:
                self._line_edit.setVisible(False)
                self._add_button.setVisible(True)

        return super(MNewTag, self).eventFilter(widget, event)
