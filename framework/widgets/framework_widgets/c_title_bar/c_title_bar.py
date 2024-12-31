import os.path

from PySide6.QtCore import QSize, Signal, QDateTime, QTimer
from PySide6.QtGui import QCursor, Qt, QColor
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QGraphicsDropShadowEffect

from . import current_directory
from .c_div import CDiv
from .c_title_button import CTitleButton

_is_maximized = False
_old_size = QSize()


class CTitleBar(QWidget):
    clicked = Signal(object)
    released = Signal(object)

    def __init__(
            self,
            parent,
            app_parent,
            logo_image=os.path.join(current_directory, "logo_top_100x22.svg"),
            logo_width=100,
            dark_one="#1b1e23",
            bg_color="#343b48",
            div_color="#3c4454",
            btn_bg_color="#343b48",
            btn_bg_color_hover="#3c4454",
            btn_bg_color_pressed="#2c313c",
            icon_color="#c3ccdf",
            icon_color_hover="#dce1ec",
            icon_color_pressed="#edf0f5",
            icon_color_active="#f5f6f9",
            context_color="#6c99f4",
            text_foreground="#8a95aa",
            radius_top_left=8,
            radius_top_right=8,
            radius_bottom_left=0,
            radius_bottom_right=0,
            radius_corners=None,
            font_family="Segoe UI",
            title_size=10,
            enable_shadow=True,
            is_custom_title_bar=True,
            is_custom_title_min_btn=True,
            is_custom_title_max_btn=True,
            is_custom_title_close_btn=True,
            is_show_datetime=True
    ):
        super().__init__()

        if radius_corners is None:
            radius_corners = [1, 2, 3, 4]

        # PARAMETERS
        self._logo_image = logo_image
        self._dark_one = dark_one
        self._bg_color = bg_color
        self._div_color = div_color
        self._parent = parent
        self._app_parent = app_parent
        self._btn_bg_color = btn_bg_color
        self._btn_bg_color_hover = btn_bg_color_hover
        self._btn_bg_color_pressed = btn_bg_color_pressed
        self._context_color = context_color
        self._icon_color = icon_color
        self._icon_color_hover = icon_color_hover
        self._icon_color_pressed = icon_color_pressed
        self._icon_color_active = icon_color_active
        self._font_family = font_family
        self._title_size = title_size
        self._enable_shadow = enable_shadow
        self._text_foreground = text_foreground
        self._is_custom_title_bar = is_custom_title_bar
        self.is_custom_title_min_btn = is_custom_title_min_btn
        self.is_custom_title_max_btn = is_custom_title_max_btn
        self.is_custom_title_close_btn = is_custom_title_close_btn
        self.is_show_datetime = is_show_datetime

        # SETUP UI
        self.setup_ui()

        # ADD BG COLOR
        radius_all = [
            f"border-top-left-radius: {radius_top_left}px;",
            f"border-top-right-radius: {radius_top_right}px;",
            f"border-bottom-left-radius: {radius_bottom_left}px;",
            f"border-bottom-right-radius: {radius_bottom_right}px;"
        ]
        radius_list = []
        for c in radius_corners:
            radius_list.append(radius_all[c - 1])
        self.bg.setStyleSheet(f"background-color: {bg_color};{';'.join(radius_list)}")

        # SET LOGO AND WIDTH
        self.top_logo.setMinimumWidth(logo_width)
        self.top_logo.setMaximumWidth(logo_width)

        # self.top_logo.setPixmap(Functions.set_svg_image(logo_image))

        # MOVE WINDOW / MAXIMIZE / RESTORE
        # ///////////////////////////////////////////////////////////////
        def moveWindow(event):
            # IF MAXIMIZED CHANGE TO NORMAL
            if parent.isMaximized():
                self.maximize_restore()
                # self.resize(_old_size)
                curso_x = parent.pos().x()
                curso_y = event.globalPos().y() - QCursor.pos().y()
                parent.move(curso_x, curso_y)
            # MOVE WINDOW
            if event.buttons() == Qt.LeftButton:
                parent.move(parent.pos() + event.globalPos() - parent.dragPos)
                parent.dragPos = event.globalPos()
                event.accept()

        # MOVE APP WIDGETS
        if is_custom_title_bar:
            self.top_logo.mouseMoveEvent = moveWindow
            self.div_1.mouseMoveEvent = moveWindow
            self.title_label.mouseMoveEvent = moveWindow
            if self.is_show_datetime:
                self.time_label.mouseMoveEvent = moveWindow
            self.div_2.mouseMoveEvent = moveWindow
            self.div_3.mouseMoveEvent = moveWindow

        # MAXIMIZE / RESTORE
        if is_custom_title_bar:
            self.top_logo.mouseDoubleClickEvent = self.maximize_restore
            self.div_1.mouseDoubleClickEvent = self.maximize_restore
            self.title_label.mouseDoubleClickEvent = self.maximize_restore
            if self.is_show_datetime:
                self.time_label.mouseDoubleClickEvent = self.maximize_restore
            self.div_2.mouseDoubleClickEvent = self.maximize_restore

        # ADD WIDGETS TO TITLE BAR
        # ///////////////////////////////////////////////////////////////
        self.bg_layout.addWidget(self.top_logo)
        self.bg_layout.addWidget(self.div_1)
        self.bg_layout.addWidget(self.title_label)
        if self.is_show_datetime:
            self.bg_layout.addWidget(self.time_label)
        self.bg_layout.addWidget(self.div_2)

        # ADD BUTTONS BUTTONS
        # ///////////////////////////////////////////////////////////////
        # Functions
        if self.is_custom_title_min_btn:
            self.minimize_button.released.connect(lambda: parent.showMinimized())
        if self.is_custom_title_max_btn:
            self.maximize_restore_button.released.connect(lambda: self.maximize_restore())
        if self.is_custom_title_close_btn:
            self.close_button.released.connect(lambda: parent.close())

        # Extra BTNs layout
        self.bg_layout.addLayout(self.custom_buttons_layout)

        # ADD Buttons
        if is_custom_title_bar:
            if self.is_custom_title_min_btn:
                self.bg_layout.addWidget(self.minimize_button)
            if self.is_custom_title_max_btn:
                self.bg_layout.addWidget(self.maximize_restore_button)
            if self.is_custom_title_close_btn:
                self.bg_layout.addWidget(self.close_button)

    # ADD BUTTONS TO TITLE BAR
    # Add btns and emit signals
    # ///////////////////////////////////////////////////////////////
    def add_menus(self, parameters):
        if parameters != None and len(parameters) > 0:
            for parameter in parameters:
                _btn_icon = parameter['btn_icon']
                _btn_id = parameter['btn_id']
                _btn_tooltip = parameter['btn_tooltip']
                _is_active = parameter['is_active']

                self.menu = CTitleButton(
                    self._parent,
                    self._app_parent,
                    btn_id=_btn_id,
                    tooltip_text=_btn_tooltip,
                    dark_one=self._dark_one,
                    bg_color=self._bg_color,
                    bg_color_hover=self._btn_bg_color_hover,
                    bg_color_pressed=self._btn_bg_color_pressed,
                    icon_color=self._icon_color,
                    icon_color_hover=self._icon_color_active,
                    icon_color_pressed=self._icon_color_pressed,
                    icon_color_active=self._icon_color_active,
                    context_color=self._context_color,
                    text_foreground=self._text_foreground,
                    icon_path=_btn_icon,
                    is_active=_is_active
                )
                self.menu.clicked.connect(self.btn_clicked)
                self.menu.released.connect(self.btn_released)

                # ADD TO LAYOUT
                self.custom_buttons_layout.addWidget(self.menu)

            # ADD DIV
            if self._is_custom_title_bar:
                self.custom_buttons_layout.addWidget(self.div_3)

    # TITLE BAR MENU EMIT SIGNALS
    # ///////////////////////////////////////////////////////////////
    def btn_clicked(self):
        self.clicked.emit(self.menu)

    def btn_released(self):
        self.released.emit(self.menu)

    # SET TITLE BAR TEXT
    # ///////////////////////////////////////////////////////////////
    def set_title(self, title):
        self.title_label.setText(title)

    # MAXIMIZE / RESTORE
    # maximize and restore parent window
    # ///////////////////////////////////////////////////////////////
    def maximize_restore(self, e=None):
        global _is_maximized
        global _old_size

        # CHANGE UI AND RESIZE GRIP
        def change_ui():
            if _is_maximized:
                if hasattr(self._parent, "ui"):
                    self._parent.ui.central_widget_layout.setContentsMargins(0, 0, 0, 0)
                    self._parent.ui.window.set_stylesheet(border_radius=0, border_size=0)
                self.maximize_restore_button.set_icon(os.path.join(current_directory, "icon_restore.svg"))
            else:
                if hasattr(self._parent, "ui"):
                    self._parent.ui.central_widget_layout.setContentsMargins(10, 10, 10, 10)
                    self._parent.ui.window.set_stylesheet(border_radius=10, border_size=2)
                self.maximize_restore_button.set_icon(os.path.join(current_directory, "icon_maximize.svg"))

        # CHECK EVENT
        if self._parent.isMaximized():
            _is_maximized = False
            self._parent.showNormal()
            change_ui()
        else:
            _is_maximized = True
            _old_size = QSize(self._parent.width(), self._parent.height())
            self._parent.showMaximized()
            change_ui()

    def update_time(self):
        # 获取当前时间
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        # 更新 QLabel 的文本
        if self.is_show_datetime:
            self.time_label.setText(current_time)

    # SETUP APP
    # ///////////////////////////////////////////////////////////////
    def setup_ui(self):
        # ADD MENU LAYOUT
        self.title_bar_layout = QVBoxLayout(self)
        self.title_bar_layout.setContentsMargins(0, 0, 0, 0)

        # ADD BG
        self.bg = QFrame()

        # ADD BG LAYOUT
        self.bg_layout = QHBoxLayout(self.bg)
        self.bg_layout.setContentsMargins(10, 0, 5, 0)
        self.bg_layout.setSpacing(0)

        # DIVS
        self.div_1 = CDiv(self._div_color)
        self.div_2 = CDiv(self._div_color)
        self.div_3 = CDiv(self._div_color)

        # LEFT FRAME WITH MOVE APP
        self.top_logo = QLabel()
        self.top_logo_layout = QVBoxLayout(self.top_logo)
        self.top_logo_layout.setContentsMargins(0, 0, 0, 0)
        self.logo_svg = QSvgWidget()
        self.logo_svg.load(self._logo_image)
        self.top_logo_layout.addWidget(self.logo_svg, Qt.AlignCenter, Qt.AlignCenter)

        # TITLE LABEL
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignVCenter)
        self.title_label.setStyleSheet(f'font: {self._title_size}pt "{self._font_family}"')
        if self.is_show_datetime:
            # TIME LABEL
            self.time_label = QLabel(QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss"))
            self.time_label.setAlignment(Qt.AlignVCenter)
            self.time_label.setStyleSheet(
                f'font: {self._title_size}pt "{self._font_family}";color: {self._text_foreground};')
            # 创建一个 QTimer 用于定期更新时间
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_time)
            self.timer.start(1000)  # 每秒更新一次

        # CUSTOM BUTTONS LAYOUT
        self.custom_buttons_layout = QHBoxLayout()
        self.custom_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.custom_buttons_layout.setSpacing(3)

        # MINIMIZE BUTTON
        if self.is_custom_title_min_btn:
            self.minimize_button = CTitleButton(
                self._parent,
                self._app_parent,
                tooltip_text="Minimize app",
                dark_one=self._dark_one,
                bg_color=self._btn_bg_color,
                bg_color_hover=self._btn_bg_color_hover,
                bg_color_pressed=self._btn_bg_color_pressed,
                icon_color=self._icon_color,
                icon_color_hover=self._icon_color_hover,
                icon_color_pressed=self._icon_color_pressed,
                icon_color_active=self._icon_color_active,
                context_color=self._context_color,
                text_foreground=self._text_foreground,
                radius=6,
                icon_path=os.path.join(current_directory, "icon_minimize.svg")
            )

        # MAXIMIZE / RESTORE BUTTON
        if self.is_custom_title_max_btn:
            self.maximize_restore_button = CTitleButton(
                self._parent,
                self._app_parent,
                tooltip_text="Maximize app",
                dark_one=self._dark_one,
                bg_color=self._btn_bg_color,
                bg_color_hover=self._btn_bg_color_hover,
                bg_color_pressed=self._btn_bg_color_pressed,
                icon_color=self._icon_color,
                icon_color_hover=self._icon_color_hover,
                icon_color_pressed=self._icon_color_pressed,
                icon_color_active=self._icon_color_active,
                context_color=self._context_color,
                text_foreground=self._text_foreground,
                radius=6,
                icon_path=os.path.join(current_directory, "icon_maximize.svg")
            )

        # CLOSE BUTTON
        if self.is_custom_title_close_btn:
            self.close_button = CTitleButton(
                self._parent,
                self._app_parent,
                tooltip_text="Close app",
                dark_one=self._dark_one,
                bg_color=self._btn_bg_color,
                bg_color_hover=self._btn_bg_color_hover,
                bg_color_pressed=self._context_color,
                icon_color=self._icon_color,
                icon_color_hover=self._icon_color_hover,
                icon_color_pressed=self._icon_color_active,
                icon_color_active=self._icon_color_active,
                context_color=self._context_color,
                text_foreground=self._text_foreground,
                radius=6,
                icon_path=os.path.join(current_directory, "icon_close.svg")
            )

        # ADD TO LAYOUT
        self.title_bar_layout.addWidget(self.bg)
        if self._enable_shadow:
            self.shadow = QGraphicsDropShadowEffect()
            self.shadow.setBlurRadius(20)
            self.shadow.setXOffset(0)
            self.shadow.setYOffset(0)
            self.shadow.setColor(QColor(0, 0, 0, 160))
            self.setGraphicsEffect(self.shadow)
