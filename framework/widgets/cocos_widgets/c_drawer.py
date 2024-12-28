from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QApplication
from framework.widgets.dayu_widgets import MLabel, MToolButton, MDivider
from framework.widgets.dayu_widgets.qt import get_scale_factor


class CDrawer(QtWidgets.QWidget):
    """
    A panel which slides in from the edge of the screen.
    """

    LeftPos = "left"
    RightPos = "right"
    TopPos = "top"
    BottomPos = "bottom"

    sig_closed = QtCore.Signal()

    def __init__(self, title, position="right", closable=True, parent=None):
        super(CDrawer, self).__init__(parent)
        self.parent = parent
        self.setObjectName("message")
        self.setWindowFlags(QtCore.Qt.Popup)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)

        self._title_label = MLabel(parent=self).h4()
        self._title_label.setText(title)

        self._close_button = (
            MToolButton(parent=self).icon_only().svg("close_line.svg").small()
        )
        self._close_button.clicked.connect(self.close)
        self._close_button.setVisible(closable or False)

        self._title_extra_lay = QtWidgets.QHBoxLayout()
        _title_lay = QtWidgets.QHBoxLayout()
        _title_lay.addWidget(self._title_label)
        _title_lay.addStretch()
        _title_lay.addLayout(self._title_extra_lay)
        _title_lay.addWidget(self._close_button)

        self._bottom_lay = QtWidgets.QHBoxLayout()
        self._bottom_lay.addStretch()

        self._scroll_area = QtWidgets.QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._main_lay = QtWidgets.QVBoxLayout()
        self._main_lay.addLayout(_title_lay)
        self._main_lay.addWidget(MDivider())
        self._main_lay.addWidget(self._scroll_area)
        self._main_lay.addWidget(MDivider())
        self._main_lay.addLayout(self._bottom_lay)
        self.setLayout(self._main_lay)

        self._position = position

        self._close_timer = QtCore.QTimer(self)
        self._close_timer.setSingleShot(True)
        self._close_timer.timeout.connect(self.close)
        self._close_timer.timeout.connect(self.sig_closed)
        self._close_timer.setInterval(300)
        self._is_first_close = True

        self._pos_ani = QtCore.QPropertyAnimation(self)
        self._pos_ani.setTargetObject(self)
        self._pos_ani.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self._pos_ani.setDuration(300)
        self._pos_ani.setPropertyName(b"pos")

        self._opacity_ani = QtCore.QPropertyAnimation()
        self._opacity_ani.setTargetObject(self)
        self._opacity_ani.setDuration(300)
        self._opacity_ani.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self._opacity_ani.setPropertyName(b"windowOpacity")
        self._opacity_ani.setStartValue(0.0)
        self._opacity_ani.setEndValue(1.0)

    def set_widget(self, widget):
        self._scroll_area.setWidget(widget)

    def add_widget_to_bottom(self, button):
        self._bottom_lay.addWidget(button)

    def add_widget_to_top(self, button):
        self._title_extra_lay.addWidget(button)

    def _fade_out(self):
        self._pos_ani.setDirection(QtCore.QAbstractAnimation.Backward)
        self._pos_ani.start()
        self._opacity_ani.setDirection(QtCore.QAbstractAnimation.Backward)
        self._opacity_ani.start()

    def _fade_in(self):
        self._pos_ani.start()
        self._opacity_ani.start()

    def _calculate_global_position(self, widget):
        """递归计算全局坐标"""
        if widget.parentWidget() is None:
            return widget.geometry().topLeft()
        else:
            parent_pos = self._calculate_global_position(widget.parentWidget())
            return widget.geometry().topLeft() + parent_pos

    def _set_proper_position(self):
        if self.parent is None:
            parent_geo = QApplication.primaryScreen().geometry()
        else:
            parent_geo = self.parent.geometry()
            parent_pos = self._calculate_global_position(self.parent)
            parent_geo.moveTo(parent_pos)

        if self._position == CDrawer.LeftPos:
            pos = parent_geo.topLeft()
            target_x = pos.x()
            target_y = pos.y()
            self.setFixedHeight(parent_geo.height())
            self._pos_ani.setStartValue(QtCore.QPoint(target_x - self.width(), target_y))
            self._pos_ani.setEndValue(QtCore.QPoint(target_x, target_y))
        elif self._position == CDrawer.RightPos:
            pos = parent_geo.topRight()
            target_x = pos.x() - self.width()
            target_y = pos.y()
            self.setFixedHeight(parent_geo.height())
            self._pos_ani.setStartValue(QtCore.QPoint(target_x + self.width(), target_y))
            self._pos_ani.setEndValue(QtCore.QPoint(target_x, target_y))
        elif self._position == CDrawer.TopPos:
            pos = parent_geo.topLeft()
            target_x = pos.x()
            target_y = pos.y()
            self.setFixedWidth(parent_geo.width())
            self._pos_ani.setStartValue(QtCore.QPoint(target_x, target_y - self.height()))
            self._pos_ani.setEndValue(QtCore.QPoint(target_x, target_y))
        elif self._position == CDrawer.BottomPos:
            pos = parent_geo.bottomLeft()
            target_x = pos.x()
            target_y = pos.y() - self.height()
            self.setFixedWidth(parent_geo.width())
            self._pos_ani.setStartValue(QtCore.QPoint(target_x, target_y + self.height()))
            self._pos_ani.setEndValue(QtCore.QPoint(target_x, target_y))

    def set_dayu_position(self, value):
        self._position = value
        scale_x, _ = get_scale_factor()
        if value in [CDrawer.BottomPos, CDrawer.TopPos]:
            self.setFixedHeight(200 * scale_x)
        else:
            self.setFixedWidth(200 * scale_x)

    def get_dayu_position(self):
        return self._position

    dayu_position = QtCore.Property(str, get_dayu_position, set_dayu_position)

    def left(self):
        self.set_dayu_position(CDrawer.LeftPos)
        return self

    def right(self):
        self.set_dayu_position(CDrawer.RightPos)
        return self

    def top(self):
        self.set_dayu_position(CDrawer.TopPos)
        return self

    def bottom(self):
        self.set_dayu_position(CDrawer.BottomPos)
        return self

    def show(self):
        self.reset()
        super(CDrawer, self).show()
        self._set_proper_position()
        self._fade_in()
        self.activateWindow()

    def closeEvent(self, event):
        if self._is_first_close:
            self._is_first_close = False
            self._close_timer.start()
            self._fade_out()
            event.ignore()
        else:
            event.accept()

    def reset(self):
        self._is_first_close = True
        self._close_timer.stop()
        self._pos_ani.setDirection(QtCore.QAbstractAnimation.Forward)
        self._opacity_ani.setDirection(QtCore.QAbstractAnimation.Forward)
