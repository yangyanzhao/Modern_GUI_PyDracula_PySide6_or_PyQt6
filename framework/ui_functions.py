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
import random

from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QEvent, QTimer, Qt, QSize
from PySide6.QtGui import QColor, QIcon, QCursor, QFont, QPixmap
from PySide6.QtWidgets import QPushButton, QGraphicsDropShadowEffect, QSizeGrip, QSizePolicy

from framework.app_settings import Settings
from framework.widgets.cocos_widgets import CustomGrip
from resources.framework.icons import icons

# MAIN FILE
# ///////////////////////////////////////////////////////////////

# GLOBALS
# ///////////////////////////////////////////////////////////////
GLOBAL_STATE = False
GLOBAL_TITLE_BAR = True


class UIFunctions:
    # MAXIMIZE/RESTORE
    # ///////////////////////////////////////////////////////////////   z
    @staticmethod
    def maximize_restore(self):
        global GLOBAL_STATE
        status = GLOBAL_STATE
        if status == False:
            self.showMaximized()
            GLOBAL_STATE = True
            self.appMargins.setContentsMargins(0, 0, 0, 0)
            self.contentTopBg.rightButtons.maximizeRestoreAppBtn.setToolTip("Restore")
            self.contentTopBg.rightButtons.maximizeRestoreAppBtn.setIcon(
                QIcon(icons['icon_restore.png']))
            self.bottomBar.frame_size_grip.hide()
            self.left_grip.hide()
            self.right_grip.hide()
            self.top_grip.hide()
            self.bottom_grip.hide()
        else:
            GLOBAL_STATE = False
            self.showNormal()
            self.resize(self.width() + 1, self.height() + 1)
            self.appMargins.setContentsMargins(0, 0, 0, 0)
            self.contentTopBg.rightButtons.maximizeRestoreAppBtn.setToolTip("Maximize")
            self.contentTopBg.rightButtons.maximizeRestoreAppBtn.setIcon(
                QIcon(icons['icon_maximize.png']))
            self.bottomBar.frame_size_grip.show()
            self.left_grip.show()
            self.right_grip.show()
            self.top_grip.show()
            self.bottom_grip.show()

    # RETURN STATUS
    # ///////////////////////////////////////////////////////////////
    @staticmethod
    def returStatus(self):
        return GLOBAL_STATE

    # SET STATUS
    # ///////////////////////////////////////////////////////////////
    @staticmethod
    def setStatus(self, status):
        global GLOBAL_STATE
        GLOBAL_STATE = status

    # TOGGLE MENU
    # ///////////////////////////////////////////////////////////////
    @staticmethod
    def toggleMenu(self, enable):
        if enable:
            # GET WIDTH
            width = self.leftMenuBg.width()
            maxExtend = Settings.MENU_WIDTH
            standard = 60

            # SET MAX WIDTH
            if width == 60:
                widthExtended = maxExtend
            else:
                widthExtended = standard

            # ANIMATION
            self.animation = QPropertyAnimation(self.leftMenuBg, b"minimumWidth")
            self.animation.setDuration(Settings.TIME_ANIMATION)
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation.start()

    # TOGGLE LEFT BOX
    # ///////////////////////////////////////////////////////////////
    @staticmethod
    def toggleLeftBox(self, enable):
        if enable:
            # GET WIDTH
            width = self.extraLeftBox.width()
            widthRightBox = self.extraRightBox.width()
            maxExtend = Settings.LEFT_BOX_WIDTH
            color = Settings.BTN_LEFT_BOX_COLOR
            standard = 0

            # GET BTN STYLE
            style = self.leftMenuBg.leftMenuFrame.toggleLeftBox.styleSheet()

            # SET MAX WIDTH
            if width == 0:
                widthExtended = maxExtend
                # SELECT BTN
                self.leftMenuBg.leftMenuFrame.toggleLeftBox.setStyleSheet(style + color)
                if widthRightBox != 0:
                    style = self.contentTopBg.rightButtons.settingsTopBtn.styleSheet()
                    self.contentTopBg.rightButtons.settingsTopBtn.setStyleSheet(
                        style.replace(Settings.BTN_RIGHT_BOX_COLOR, ''))
            else:
                widthExtended = standard
                # RESET BTN
                self.leftMenuBg.leftMenuFrame.toggleLeftBox.setStyleSheet(style.replace(color, ''))

        UIFunctions.start_box_animation(self, width, widthRightBox, "left")

    # TOGGLE RIGHT BOX
    # ///////////////////////////////////////////////////////////////
    @staticmethod
    def toggleRightBox(self, enable):
        if enable:
            # GET WIDTH
            width = self.extraRightBox.width()
            widthLeftBox = self.extraLeftBox.width()
            maxExtend = Settings.RIGHT_BOX_WIDTH
            color = Settings.BTN_RIGHT_BOX_COLOR
            standard = 0

            # GET BTN STYLE
            style = self.contentTopBg.rightButtons.settingsTopBtn.styleSheet()

            # SET MAX WIDTH
            if width == 0:
                widthExtended = maxExtend
                # SELECT BTN
                self.contentTopBg.rightButtons.settingsTopBtn.setStyleSheet(style + color)
                if widthLeftBox != 0:
                    style = self.leftMenuBg.leftMenuFrame.toggleLeftBox.styleSheet()
                    self.leftMenuBg.leftMenuFrame.toggleLeftBox.setStyleSheet(
                        style.replace(Settings.BTN_LEFT_BOX_COLOR, ''))
            else:
                widthExtended = standard
                # RESET BTN
                self.contentTopBg.rightButtons.settingsTopBtn.setStyleSheet(style.replace(color, ''))

            UIFunctions.start_box_animation(self, widthLeftBox, width, "right")

    @staticmethod
    def start_box_animation(self, left_box_width, right_box_width, direction):
        right_width = 0
        left_width = 0

        # Check values
        if left_box_width == 0 and direction == "left":
            left_width = 240
        else:
            left_width = 0
        # Check values
        if right_box_width == 0 and direction == "right":
            right_width = 240
        else:
            right_width = 0

            # ANIMATION LEFT BOX
        self.left_box = QPropertyAnimation(self.extraLeftBox, b"minimumWidth")
        self.left_box.setDuration(Settings.TIME_ANIMATION)
        self.left_box.setStartValue(left_box_width)
        self.left_box.setEndValue(left_width)
        self.left_box.setEasingCurve(QEasingCurve.InOutQuart)

        # ANIMATION RIGHT BOX        
        self.right_box = QPropertyAnimation(self.extraRightBox, b"minimumWidth")
        self.right_box.setDuration(Settings.TIME_ANIMATION)
        self.right_box.setStartValue(right_box_width)
        self.right_box.setEndValue(right_width)
        self.right_box.setEasingCurve(QEasingCurve.InOutQuart)

        # GROUP ANIMATION
        self.group = QParallelAnimationGroup()
        self.group.addAnimation(self.left_box)
        self.group.addAnimation(self.right_box)
        self.group.start()

    # SELECT/DESELECT MENU
    # ///////////////////////////////////////////////////////////////
    # SELECT
    @staticmethod
    def selectMenu(getStyle):
        select = getStyle + Settings.MENU_SELECTED_STYLESHEET
        return select

    # DESELECT
    @staticmethod
    def deselectMenu(getStyle):
        deselect = getStyle.replace(Settings.MENU_SELECTED_STYLESHEET, "")
        return deselect

    # START SELECTION
    @staticmethod
    def selectStandardMenu(self, widget):
        for w in self.topMenu.findChildren(QPushButton):
            if w.objectName() == widget:
                w.setStyleSheet(UIFunctions.selectMenu(w.styleSheet()))

    # RESET SELECTION
    @staticmethod
    def resetStyle(self, widget):
        for w in self.leftMenuBg.leftMenuFrame.topMenu.findChildren(QPushButton):
            if w.objectName() != widget:
                w.setStyleSheet(UIFunctions.deselectMenu(w.styleSheet()))

    # IMPORT THEMES FILES QSS/CSS
    # ///////////////////////////////////////////////////////////////
    @staticmethod
    def theme(self, file, useCustomTheme):
        if useCustomTheme:
            str = open(file, 'r').read()
            self.styleSheet.setStyleSheet(str)

    # START - GUI DEFINITIONS
    # ///////////////////////////////////////////////////////////////
    @staticmethod
    def uiDefinitions(self):
        def dobleClickMaximizeRestore(event):
            # IF DOUBLE CLICK CHANGE STATUS
            if event.type() == QEvent.MouseButtonDblClick:
                QTimer.singleShot(250, lambda: UIFunctions.maximize_restore(self))

        self.contentTopBg.leftBox.titleRightInfo.mouseDoubleClickEvent = dobleClickMaximizeRestore

        if Settings.ENABLE_CUSTOM_TITLE_BAR:
            # STANDARD TITLE BAR
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)

            # MOVE WINDOW / MAXIMIZE / RESTORE
            def moveWindow(event):
                # IF MAXIMIZED CHANGE TO NORMAL
                if UIFunctions.returStatus(self):
                    UIFunctions.maximize_restore(self)
                # MOVE WINDOW
                if event.buttons() == Qt.LeftButton:
                    new_pos = self.pos() + (event.globalPosition() - self.dragPos).toPoint()
                    self.move(new_pos)
                    self.dragPos = event.globalPosition()
                    event.accept()

            self.contentTopBg.leftBox.titleRightInfo.mouseMoveEvent = moveWindow

            # CUSTOM GRIPS
            self.left_grip = CustomGrip(self, Qt.LeftEdge, True)
            self.right_grip = CustomGrip(self, Qt.RightEdge, True)
            self.top_grip = CustomGrip(self, Qt.TopEdge, True)
            self.bottom_grip = CustomGrip(self, Qt.BottomEdge, True)

        else:
            self.appMargins.setContentsMargins(0, 0, 0, 0)
            self.minimizeAppBtn.hide()
            self.maximizeRestoreAppBtn.hide()
            self.closeAppBtn.hide()
            self.bottomBar.frame_size_grip.hide()

        # DROP SHADOW
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(17)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.bgApp.setGraphicsEffect(self.shadow)

        # RESIZE WINDOW
        self.bottomBar.sizegrip = QSizeGrip(self.bottomBar.frame_size_grip)
        self.bottomBar.sizegrip.setStyleSheet("width: 20px; height: 20px; margin 0px; padding: 0px;")

        # MINIMIZE
        self.contentTopBg.rightButtons.minimizeAppBtn.clicked.connect(lambda: self.showMinimized())

        # MAXIMIZE/RESTORE
        self.contentTopBg.rightButtons.maximizeRestoreAppBtn.clicked.connect(lambda: UIFunctions.maximize_restore(self))

        # CLOSE APPLICATION
        self.contentTopBg.rightButtons.closeAppBtn.clicked.connect(lambda: self.close())

    @staticmethod
    def resize_grips(self):
        if Settings.ENABLE_CUSTOM_TITLE_BAR:
            self.left_grip.setGeometry(0, 10, 10, self.height())
            self.right_grip.setGeometry(self.width() - 10, 10, 10, self.height())
            self.top_grip.setGeometry(0, 0, self.width(), 10)
            self.bottom_grip.setGeometry(0, self.height() - 10, self.width(), 10)

    @staticmethod
    def add_menus(self, menus_list):
        right_slash = '\\'

        for menu in menus_list:
            if menu['show_top']:
                self.btn = QPushButton(self.leftMenuBg.leftMenuFrame.topMenu)
                self.btn.setObjectName(menu['btn_id'])
                self.btn.setText(menu['btn_text'])
                self.btn.setToolTip(menu['btn_tooltip'])
                sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                sizePolicy.setHeightForWidth(self.btn.sizePolicy().hasHeightForWidth())
                self.btn.setSizePolicy(sizePolicy)
                self.btn.setMinimumSize(QSize(0, 45))
                self.btn.clicked.connect(self.buttonClick)
                font = QFont()
                font.setFamily(u"Segoe UI")
                font.setPointSize(10)
                font.setBold(False)
                font.setItalic(False)
                self.btn.setFont(font)

                self.btn.setCursor(QCursor(Qt.PointingHandCursor))
                self.btn.setLayoutDirection(Qt.LeftToRight)
                self.btn.setStyleSheet(rf"""
                        QPushButton {{
                                background-image: url({menu['btn_icon'].replace(right_slash, '/')});
                            }}
                        """)
                self.btn.update()
                # ui.btn.setIcon(QIcon(QPixmap(menu['btn_icon'])))
                self.leftMenuBg.leftMenuFrame.topMenuLayout.addWidget(self.btn)
            else:
                self.btn = QPushButton(self.leftMenuBg.leftMenuFrame.topMenu)
                self.btn.setObjectName(menu['btn_id'])
                self.btn.setText(menu['btn_text'])
                self.btn.setToolTip(menu['btn_tooltip'])
                sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                sizePolicy.setHeightForWidth(self.btn.sizePolicy().hasHeightForWidth())
                self.btn.setSizePolicy(sizePolicy)
                self.btn.setMinimumSize(QSize(0, 45))

                font = QFont()
                font.setFamily(u"Segoe UI")
                font.setPointSize(10)
                font.setBold(False)
                font.setItalic(False)
                self.btn.setFont(font)

                self.btn.setCursor(QCursor(Qt.PointingHandCursor))
                self.btn.setLayoutDirection(Qt.LeftToRight)
                self.btn.setStyleSheet(rf"""
                                        QPushButton {{
                                                background-image: url({menu['btn_icon'].replace(right_slash, '/')});
                                            }}
                                        """)
                # ui.btn.setIcon(QIcon(QPixmap(menu['btn_icon'])))
                self.leftMenuBg.leftMenuFrame.bottomMenuLayout.addWidget(self.btn)
            pass
            self.stackedWidget.addWidget(menu['interface'])

    @staticmethod
    def generate_random_color():
        """生成随机颜色"""
        return QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    # ///////////////////////////////////////////////////////////////
    # END - GUI DEFINITIONS
