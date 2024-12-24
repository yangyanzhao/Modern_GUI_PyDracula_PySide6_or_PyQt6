from PySide6.QtWidgets import QWidget, QPushButton


class ZhiHuMainInterface(QWidget):
    def __init__(self, parent=None):
        super(ZhiHuMainInterface, self).__init__(parent)
        button = QPushButton(self)
        button.setText("按钮")
        self.init_ui()

    def init_ui(self):
        pass
