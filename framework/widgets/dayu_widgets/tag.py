#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2019.8
# Email : muyanru345@163.com
###################################################################
"""
MTag
"""
from framework.widgets.dayu_widgets import dayu_theme
from framework.widgets.dayu_widgets import utils
from framework.widgets.dayu_widgets.qt import get_scale_factor
from framework.widgets.dayu_widgets.theme import QssTemplate
from framework.widgets.dayu_widgets.tool_button import MToolButton
from PySide6 import QtWidgets, QtCore


class MTag(QtWidgets.QLabel):
    """
    Tag for categorizing or markup.
    """

    sig_closed = QtCore.Signal()
    sig_clicked = QtCore.Signal()

    def __init__(self, text="", parent=None):
        super(MTag, self).__init__(text=text, parent=parent)
        self._is_pressed = False
        self._close_button = MToolButton().tiny().svg("close_line.svg").icon_only()
        self._close_button.clicked.connect(self.sig_closed)
        self._close_button.clicked.connect(self.close)
        self._close_button.setVisible(False)

        self._main_lay = QtWidgets.QHBoxLayout()
        self._main_lay.setContentsMargins(0, 0, 0, 0)
        self._main_lay.addStretch()
        self._main_lay.addWidget(self._close_button)

        self.setLayout(self._main_lay)

        self._clickable = False
        self._border = True
        self._border_style = QssTemplate(
            """
            MTag{
                font-size: @font_size_base@font_unit;
                padding: @padding_small@unit;
                color: @text_color;
                border-radius: @border_radius;
                border: 1px solid @border_color;
                background-color: @background_color;
            }
            MTag:hover{
                color: @hover_color;
            }
            """
        )
        self._no_border_style = QssTemplate(
            """
            MTag{
                font-size: @font_size_base@font_unit;
                padding: @padding@unit;
                border-radius: @border_radius;
                color: @text_color;
                border: 0 solid @border_color;
                background-color: @background_color;
            }
            MTag:hover{
                background-color:@hover_color;
            }
        """
        )
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        self._color = None
        self.set_dayu_color(dayu_theme.secondary_text_color)

    def minimumSizeHint(self, *args, **kwargs):
        """Override minimumSizeHint for expand width when the close button is visible."""
        orig = super(MTag, self).minimumSizeHint(*args, **kwargs)
        orig.setWidth(
            orig.width() + (dayu_theme.tiny if self._close_button.isVisible() else 0)
        )
        return orig

    def get_dayu_color(self):
        """Get tag's color"""
        return self._color

    def set_dayu_color(self, value):
        """Set Tag primary color."""
        self._color = value
        self._update_style()

    def _update_style(self):
        scale_x, _ = get_scale_factor()
        if self._border:
            self.setStyleSheet(
                self._border_style.substitute(
                    padding_small=3 * scale_x,
                    font_size_base=dayu_theme.font_size_base,
                    font_unit=dayu_theme.font_unit,
                    unit=dayu_theme.unit,
                    background_color=utils.fade_color(self._color, "15%"),
                    border_radius=dayu_theme.border_radius_base,
                    border_color=utils.fade_color(self._color, "35%"),
                    hover_color=utils.generate_color(self._color, 5),
                    text_color=self._color,
                )
            )
        else:
            self.setStyleSheet(
                self._no_border_style.substitute(
                    padding=4 * scale_x,
                    font_size_base=dayu_theme.font_size_base,
                    font_unit=dayu_theme.font_unit,
                    unit=dayu_theme.unit,
                    background_color=utils.generate_color(self._color, 6),
                    border_radius=dayu_theme.border_radius_base,
                    border_color=utils.generate_color(self._color, 6),
                    hover_color=utils.generate_color(self._color, 5),
                    text_color=dayu_theme.text_color_inverse,
                )
            )

    dayu_color = QtCore.Property(str, get_dayu_color, set_dayu_color)

    def mousePressEvent(self, event):
        """Override mousePressEvent to flag _is_pressed."""
        if event.button() == QtCore.Qt.LeftButton:
            self._is_pressed = True
        return super(MTag, self).mousePressEvent(event)

    def leaveEvent(self, event):
        """Override leaveEvent to reset _is_pressed flag."""
        self._is_pressed = False
        return super(MTag, self).leaveEvent(event)

    def mouseReleaseEvent(self, event):
        """Override mouseReleaseEvent to emit sig_clicked signal."""
        if event.button() == QtCore.Qt.LeftButton and self._is_pressed:
            if self._clickable:
                self.sig_clicked.emit()
        self._is_pressed = False
        return super(MTag, self).mouseReleaseEvent(event)

    def closeable(self):
        """Set Tag can be closed and show the close icon button."""
        self._close_button.setVisible(True)
        return self

    def clickable(self):
        """Set Tag can be clicked and change the cursor to pointing-hand shape when enter."""
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self._clickable = True
        return self

    def no_border(self):
        """Set Tag style is border or fill."""
        self._border = False
        self._update_style()
        return self

    def coloring(self, color):
        """Same as set_dayu_color. Support chain."""
        self.set_dayu_color(color)
        return self
