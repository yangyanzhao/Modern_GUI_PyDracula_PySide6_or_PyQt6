import sys

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon, QFont, QCursor
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication, QPushButton, QSizePolicy

from resources.framework.icons import icons
from resources.framework.images import images


class DemoHomeInterface(QWidget):
    def __init__(self, parent=None):
        super(DemoHomeInterface, self).__init__(parent)
        self.setObjectName(u"demo_home_interface")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        self.label = QLabel()
        self.label.setPixmap(QPixmap(images['PyDracula_vertical.png']))
        layout.addWidget(self.label)

        menu = {
            "btn_icon": icons["cil-home.png"],  # 图标
            "btn_id": "btn_home",  # 按钮ID
            "btn_text": "Home",  # 按钮文本
            "btn_tooltip": "Home page",  # 提示
            "show_top": True,  # 是否显示在顶部
            "is_active": True  # 是否激活
        }
        self.btn = QPushButton(self)
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
        self.btn.setStyleSheet(r"""
        QPushButton {
                background-image: url(D:/pythonwork/Modern_GUI_PyDracula_PySide6_or_PyQt6/resources/framework/icons/cil-gamepad.png);
            }
        """)
        self.btn.setIcon(QIcon(
            QPixmap(rf'D:\pythonwork\Modern_GUI_PyDracula_PySide6_or_PyQt6\resources\framework\icons\cil-home.png')))
        layout.addWidget(self.btn)

        self.show()

from framework.resources_rc import *
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(icons["icon.ico"]))
    window = DemoHomeInterface()
    sys.exit(app.exec())
