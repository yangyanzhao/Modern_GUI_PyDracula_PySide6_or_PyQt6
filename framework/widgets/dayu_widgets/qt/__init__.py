# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2019.3
# Email : muyanru345@163.com
###################################################################

# Import future modules
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Import built-in modules
import contextlib
import signal
import sys

# Import third-party modules
import six
from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtGui import QGuiApplication, QColor, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize


class MCacheDict(object):
    _render = QSvgRenderer()

    def __init__(self, cls):
        super(MCacheDict, self).__init__()
        self.cls = cls
        self._cache_pix_dict = {}

    def _render_svg(self, svg_path, replace_color=None):
        # Import local modules
        from framework.widgets.dayu_widgets import dayu_theme

        replace_color = replace_color or dayu_theme.icon_color
        if (self.cls is QtGui.QIcon) and (replace_color is None):
            return QtGui.QIcon(svg_path)
        with open(svg_path, "r") as f:
            data_content = f.read()
            if replace_color is not None:
                data_content = data_content.replace("#555555", replace_color)
            self._render.load(QtCore.QByteArray(six.b(data_content)))
            pix = QtGui.QPixmap(128, 128)
            pix.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(pix)
            self._render.render(painter)
            painter.end()
            if self.cls is QtGui.QPixmap:
                return pix
            else:
                return self.cls(pix)

    def __call__(self, path, color=None):
        # Import local modules
        from framework.widgets.dayu_widgets import utils

        full_path = utils.get_static_file(path)
        if full_path is None:
            return self.cls()
        key = "{}{}".format(full_path.lower(), color or "")
        pix_map = self._cache_pix_dict.get(key, None)
        if pix_map is None:
            if full_path.endswith("svg"):
                pix_map = self._render_svg(full_path, color)
            else:
                pix_map = self.cls(full_path)
            self._cache_pix_dict.update({key: pix_map})
        return pix_map


def get_scale_factor():
    primary_screen = QGuiApplication.primaryScreen()
    if primary_screen:
        logical_dpi_x = primary_screen.logicalDotsPerInchX()
        logical_dpi_y = primary_screen.logicalDotsPerInchY()
        standard_dpi = 96.0
        scale_factor_x = logical_dpi_x / standard_dpi
        scale_factor_y = logical_dpi_y / standard_dpi
        return scale_factor_x, scale_factor_y
    return 1.0, 1.0


@contextlib.contextmanager
def application(*args):
    app = QtWidgets.QApplication.instance()

    if not app:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        app = QtWidgets.QApplication(sys.argv)
        yield app
        app.exec_()
    else:
        yield app


MPixmap = MCacheDict(QtGui.QPixmap)
MIcon = MCacheDict(QtGui.QIcon)


class MIconWidget(QWidget):
    def __init__(self, icon=None, size=QSize(32, 32), color=QColor("black"), parent=None):
        """
        自定义 QIconWidget，用于直接显示图标，并支持修改图标颜色。

        :param icon: QIcon 对象或图标文件路径（str）
        :param size: 图标显示的大小，默认为 64x64
        :param color: 图标的颜色，默认为黑色
        :param parent: 父控件
        """
        super().__init__(parent)
        self.setFixedSize(size)
        # 初始化布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # 创建 QLabel 用于显示图标
        self.icon_label = QLabel(self)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.icon_label)

        # 设置默认图标大小和颜色
        self.icon_size = size
        self.color = color

        # 设置图标
        self.set_icon(icon)

    def set_icon(self, icon):
        """
        设置图标。

        :param icon: QIcon 对象或图标文件路径（str）
        """
        if isinstance(icon, QIcon):
            self.icon = icon
        elif isinstance(icon, str):
            self.icon = QIcon(icon)
        else:
            self.icon = QIcon()  # 如果传入的图标无效，则使用空图标

        # 更新显示
        self.update_icon()

    def set_icon_size(self, size):
        """
        设置图标显示的大小。

        :param size: QSize 对象或 (width, height) 元组
        """
        if isinstance(size, QSize):
            self.icon_size = size
        elif isinstance(size, (tuple, list)):
            self.icon_size = QSize(size[0], size[1])
        else:
            raise ValueError("size 必须是 QSize 对象或 (width, height) 元组")

        # 更新显示
        self.update_icon()

    def set_color(self, color):
        """
        设置图标的颜色。

        :param color: QColor 对象或颜色名称（str）
        """
        if isinstance(color, QColor):
            self.color = color
        elif isinstance(color, str):
            self.color = QColor(color)
        else:
            raise ValueError("color 必须是 QColor 对象或颜色名称（str）")

        # 更新显示
        self.update_icon()

    def update_icon(self):
        """
        更新图标的显示。
        """
        if self.icon.isNull():
            self.icon_label.clear()
        else:
            # 将 QIcon 转换为 QPixmap
            pixmap = self.icon.pixmap(self.icon_size)

            # 创建一个新的 QPixmap 用于绘制
            colored_pixmap = QPixmap(pixmap.size())
            colored_pixmap.fill(Qt.transparent)

            # 使用 QPainter 修改颜色
            painter = QPainter(colored_pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(colored_pixmap.rect(), self.color)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()

            # 设置修改后的 QPixmap 到 QLabel
            self.icon_label.setPixmap(colored_pixmap)

            # 设置 QLabel 的大小与 QIcon 的大小一致
            self.icon_label.setFixedSize(colored_pixmap.size())

    def resizeEvent(self, event):
        """
        重写 resizeEvent，使图标自动适应控件大小。
        """
        super().resizeEvent(event)
        # 如果控件大小发生变化，保持 QLabel 的大小与 QIcon 的大小一致
        self.update_icon()
