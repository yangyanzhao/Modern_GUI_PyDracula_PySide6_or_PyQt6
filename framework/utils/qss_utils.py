from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PySide6 import QtWidgets, QtGui
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel

from framework.widgets.dayu_widgets import dayu_theme


def apply_focus_shadow(widget, shadow_color=None):
    """
    聚焦添加阴影，失焦移除
    Add shadow effect for the given widget when it is focused.
    When focus in the widget, enable shadow effect.
    When focus out the widget, disable shadow effect.
    """
    # Save the original focusInEvent and focusOutEvent methods
    original_focus_in_event = widget.focusInEvent
    original_focus_out_event = widget.focusOutEvent

    def _focus_in_event(event):
        if not widget.graphicsEffect():
            shadow_effect = QtWidgets.QGraphicsDropShadowEffect(widget)
            dayu_type = widget.property("dayu_type")
            if not shadow_color:
                color = vars(dayu_theme).get("{}_color".format(dayu_type or "primary"), "primary_color")
            else:
                color = shadow_color
            shadow_effect.setColor(QtGui.QColor(color))
            shadow_effect.setOffset(0, 0)
            shadow_effect.setBlurRadius(5)
            shadow_effect.setEnabled(False)
            widget.setGraphicsEffect(shadow_effect)
        if widget.isEnabled():
            widget.graphicsEffect().setEnabled(True)
        original_focus_in_event(event)  # Call the original focusInEvent with only the event argument

    def _focus_out_event(event):
        if widget.graphicsEffect():
            widget.graphicsEffect().setEnabled(False)
        original_focus_out_event(event)  # Call the original focusOutEvent with only the event argument

    # Replace the original focusInEvent and focusOutEvent with the new ones
    widget.focusInEvent = _focus_in_event
    widget.focusOutEvent = _focus_out_event


def apply_hover_shadow_mixin(widget, shadow_color=None):
    """
    悬停添加阴影，离开移除
    Add shadow effect for the given widget when it is hovered.
    When mouse enter the widget, enable shadow effect.
    When mouse leave the widget, disable shadow effect.
    """
    # Save the original enterEvent and leaveEvent methods
    original_enter_event = widget.enterEvent
    original_leave_event = widget.leaveEvent

    def _enter_event(event):
        if not widget.graphicsEffect():
            shadow_effect = QtWidgets.QGraphicsDropShadowEffect(widget)
            dayu_type = widget.property("type")
            if not shadow_color:
                color = vars(dayu_theme).get("{}_color".format(dayu_type or "primary"), "primary_color")
            else:
                color = shadow_color
            shadow_effect.setColor(QtGui.QColor(color))
            shadow_effect.setOffset(0, 0)
            shadow_effect.setBlurRadius(5)
            shadow_effect.setEnabled(False)
            widget.setGraphicsEffect(shadow_effect)
        if widget.isEnabled():
            widget.graphicsEffect().setEnabled(True)
        original_enter_event(event)  # Call the original enterEvent with only the event argument

    def _leave_event(event):
        if widget.graphicsEffect():
            widget.graphicsEffect().setEnabled(False)
        original_leave_event(event)  # Call the original leaveEvent with only the event argument

    # Replace the original enterEvent and leaveEvent with the new ones
    widget.enterEvent = _enter_event
    widget.leaveEvent = _leave_event


def set_label_background_image(label: QLabel, pixmap: QPixmap):
    """
    设置背景图
    按照图片的原始比例进行缩放，刚好覆盖label，多余的剪裁掉。
    :return:
    """

    def calculate_scale_ratio(image_width, image_height, widget_width, widget_height):
        # 计算缩放比例
        scale_ratio = max(widget_width / image_width, widget_height / image_height)
        return scale_ratio

    scale_ratio = calculate_scale_ratio(pixmap.width(), pixmap.height(),
                                        label.width(),
                                        label.height())

    scaled_width = int(pixmap.width() * scale_ratio)
    scaled_height = int(pixmap.height() * scale_ratio)
    scaled_pixmap = pixmap.scaled(scaled_width, scaled_height)
    # 设置背景图像
    label.setPixmap(scaled_pixmap)
