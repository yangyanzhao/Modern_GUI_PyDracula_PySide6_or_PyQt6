# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////
import sys

from PySide6 import QtAsyncio, QtWidgets
from PySide6.QtWidgets import QLineEdit, QApplication

# IMPORT QT CORE
# /////////////////////

# STYLE
# ///////////////////////////////////////////////////////////////
style = '''
QLineEdit {{
	background-color: {_bg_color};
	border-radius: {_radius}px;
	border: {_border_size}px solid transparent;
	padding-left: 10px;
    padding-right: 10px;
	selection-color: {_selection_color};
	selection-background-color: {_context_color};
    color: {_color};
}}
QLineEdit:focus {{
	border: {_border_size}px solid {_context_color};
    background-color: {_bg_color_active};
}}
'''


# PY PUSH BUTTON
# ///////////////////////////////////////////////////////////////
class CLineEdit(QLineEdit):
    def __init__(
            self,
            text="",
            place_holder_text="",
            radius=8,
            border_size=2,
            color="#FFF",
            selection_color="#FFF",
            bg_color="#333",
            bg_color_active="#222",
            context_color="#00ABE8"
    ):
        """

        :param text: 默认输入
        :param place_holder_text: 占位符
        :param radius: 圆角
        :param border_size: 边框宽度
        :param color: 文本颜色
        :param selection_color: 选中时字体颜色
        :param bg_color: 未聚焦时背景颜色
        :param bg_color_active: 聚焦时背景颜色
        :param context_color: 整体颜色（可见的边框颜色）
        """
        super().__init__()

        # PARAMETERS
        if text:
            self.setText(text)
        if place_holder_text:
            self.setPlaceholderText(place_holder_text)

        # SET STYLESHEET
        self.set_stylesheet(
            radius,
            border_size,
            color,
            selection_color,
            bg_color,
            bg_color_active,
            context_color
        )

    # SET STYLESHEET
    def set_stylesheet(
            self,
            radius,
            border_size,
            color,
            selection_color,
            bg_color,
            bg_color_active,
            context_color
    ):
        # APPLY STYLESHEET
        style_format = style.format(
            _radius=radius,
            _border_size=border_size,
            _color=color,
            _selection_color=selection_color,
            _bg_color=bg_color,
            _bg_color_active=bg_color_active,
            _context_color=context_color
        )
        self.setStyleSheet(style_format)