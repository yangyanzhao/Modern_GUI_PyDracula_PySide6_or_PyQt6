from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from resources.framework.images import images


class DemoNewPageInterface(QWidget):
    def __init__(self, parent=None):
        super(DemoNewPageInterface, self).__init__(parent)
        self.setObjectName(u"demo_new_page_interface")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        self.label = QLabel()
        self.label.setPixmap(QPixmap(images['PyDracula_vertical.png']))
        layout.addWidget(self.label)
