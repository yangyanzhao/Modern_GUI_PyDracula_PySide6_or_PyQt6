from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QDateTimeEdit
from PySide6.QtCore import QDateTime

from widgets.cocos_widgets.c_calendar import CCalendarWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口布局
        self.setWindowTitle("QDateTimeEdit 示例")
        self.setGeometry(100, 100, 300, 200)
        layout = QVBoxLayout()

        # 创建 QDateTimeEdit 控件
        self.datetime_edit = QDateTimeEdit(self)
        self.datetime_edit.setCalendarPopup(True)

        # 设置默认日期为当前日期
        current_datetime = QDateTime.currentDateTime()
        self.datetime_edit.setDateTime(current_datetime)

        # 自定义日历控件
        self.custom_calendar = CCalendarWidget(self.datetime_edit, self)
        self.datetime_edit.setCalendarWidget(self.custom_calendar)

        # 添加 QDateTimeEdit 到布局
        layout.addWidget(self.datetime_edit)

        # 设置布局
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
