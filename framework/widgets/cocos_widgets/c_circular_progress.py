import sys

from PySide6 import QtAsyncio, QtWidgets
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QPainter, QFont, QPen
from PySide6.QtWidgets import QWidget, QGraphicsDropShadowEffect, QApplication


class CCircularProgress(QWidget):
    def __init__(
            self,
            value=0,
            progress_width=10,
            is_rounded=True,
            max_value=100,
            progress_color="#ff79c6",
            enable_text=True,
            font_family="Segoe UI",
            font_size=12,
            suffix="%",
            text_color="#ff79c6",
            enable_bg=True,
            bg_color="#44475a"
    ):
        """

        :param value: 进度
        :param progress_width: 环形宽度
        :param is_rounded:
        :param max_value: 最大值
        :param progress_color: 进度颜色
        :param enable_text: 是否文字
        :param font_family: 字体
        :param font_size: 字体大小
        :param suffix: 文字后缀
        :param text_color: 字体颜色
        :param enable_bg: 是否背景
        :param bg_color: 背景颜色
        """
        QWidget.__init__(self)

        # CUSTOM PROPERTIES
        self.value = value
        self.progress_width = progress_width
        self.progress_rounded_cap = is_rounded
        self.max_value = max_value
        self.progress_color = progress_color
        # Text
        self.enable_text = enable_text
        self.font_family = font_family
        self.font_size = font_size
        self.suffix = suffix
        self.text_color = text_color
        # BG
        self.enable_bg = enable_bg
        self.bg_color = bg_color

    # ADD DROPSHADOW
    def add_shadow(self, enable):
        if enable:
            self.shadow = QGraphicsDropShadowEffect(self)
            self.shadow.setBlurRadius(15)
            self.shadow.setXOffset(0)
            self.shadow.setYOffset(0)
            self.shadow.setColor(QColor(0, 0, 0, 80))
            self.setGraphicsEffect(self.shadow)

    # SET VALUE
    def set_value(self, value):
        self.value = value
        self.repaint()  # Render progress bar after change value

    # PAINT EVENT (DESIGN YOUR CIRCULAR PROGRESS HERE)
    def paintEvent(self, e):
        # SET PROGRESS PARAMETERS
        width = self.width() - self.progress_width
        height = self.height() - self.progress_width
        margin = self.progress_width / 2
        value = self.value * 360 / self.max_value

        # PAINTER
        paint = QPainter()
        paint.begin(self)
        paint.setRenderHint(QPainter.Antialiasing)  # remove pixelated edges
        paint.setFont(QFont(self.font_family, self.font_size))

        # CREATE RECTANGLE
        rect = QRect(0, 0, self.width(), self.height())
        paint.setPen(Qt.NoPen)

        # PEN
        pen = QPen()
        pen.setWidth(self.progress_width)
        # Set Round Cap
        if self.progress_rounded_cap:
            pen.setCapStyle(Qt.RoundCap)

        # ENABLE BG
        if self.enable_bg:
            pen.setColor(QColor(self.bg_color))
            paint.setPen(pen)
            paint.drawArc(margin, margin, width, height, 0, 360 * 16)

            # CREATE ARC / CIRCULAR PROGRESS
        pen.setColor(QColor(self.progress_color))
        paint.setPen(pen)
        paint.drawArc(margin, margin, width, height, -90 * 16, -value * 16)

        # CREATE TEXT
        if self.enable_text:
            pen.setColor(QColor(self.text_color))
            paint.setPen(pen)
            paint.drawText(rect, Qt.AlignCenter, f"{self.value}{self.suffix}")

        # END
        paint.end()