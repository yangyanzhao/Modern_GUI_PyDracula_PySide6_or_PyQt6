import sys
from PySide6.QtWidgets import QApplication, QMainWindow

from widgets.cocos_widgets.c_grips import CGrips


# 假设 PyGrips 和 Widgets 类已经在同一个文件中定义
# 这里我们直接使用上面提供的代码

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resizable Window with PyGrips")
        self.setGeometry(100, 100, 800, 600)

        # 创建 CGrips 实例
        self.top_grip = CGrips(parent=self, position="top", disable_color=False)
        self.bottom_grip = CGrips(self, "bottom")
        self.left_grip = CGrips(self, "left")
        self.right_grip = CGrips(self, "right")
        self.top_left_grip = CGrips(self, "top_left")
        self.top_right_grip = CGrips(self, "top_right")
        self.bottom_left_grip = CGrips(self, "bottom_left")
        self.bottom_right_grip = CGrips(self, "bottom_right")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
