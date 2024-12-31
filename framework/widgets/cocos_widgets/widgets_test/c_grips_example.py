import sys
from PySide6.QtWidgets import QApplication, QMainWindow

from framework.widgets.cocos_widgets import CGrips


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resizable Window with PyGrips")
        self.setGeometry(100, 100, 800, 600)

        # 创建 CGrips 实例
        disable_color = True
        self.top_grip = CGrips(parent=self, position="top", disable_color=disable_color)
        self.bottom_grip = CGrips(self, "bottom", disable_color=disable_color)
        self.left_grip = CGrips(self, "left", disable_color=disable_color)
        self.right_grip = CGrips(self, "right", disable_color=disable_color)
        self.top_left_grip = CGrips(self, "top_left", disable_color=disable_color)
        self.top_right_grip = CGrips(self, "top_right", disable_color=disable_color)
        self.bottom_left_grip = CGrips(self, "bottom_left", disable_color=disable_color)
        self.bottom_right_grip = CGrips(self, "bottom_right", disable_color=disable_color)

    def resizeEvent(self, event):
        # Update Size Grips
        self.left_grip.setGeometry(0, 10, 10, self.height())
        self.right_grip.setGeometry(self.width() - 10, 10, 10, self.height())
        self.top_grip.setGeometry(0, 0, self.width(), 10)
        self.bottom_grip.setGeometry(0, self.height() - 10, self.width(), 10)

        self.top_left_grip.setGeometry(5, 5, 20, 20)
        self.top_right_grip.setGeometry(self.width() - 25, 5, 20, 20)
        self.bottom_left_grip.setGeometry(5, self.height() - 25, 20, 20)
        self.bottom_right_grip.setGeometry(self.width() - 25, self.height() - 25, 20, 20)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
