from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QDateTimeEdit, QCalendarWidget
from PySide6.QtCore import QDate, QDateTime
from widgets.dayu_widgets import MPushButton


class CCalendarWidget(QCalendarWidget):
    def __init__(self, datetime_edit, parent=None):
        super().__init__(parent)

        # 保存 QDateTimeEdit 的引用
        self.datetime_edit = datetime_edit

        # 创建“此刻”按钮
        self.now_button = MPushButton("此刻", parent=self).small()
        self.now_button.clicked.connect(self.set_current_datetime)

        # 调整按钮位置
        self.now_button.setGeometry(25, 0, 60, 30)

    def set_current_datetime(self):
        """
        将日期设置为当前日期和时间
        """
        current_datetime = QDateTime.currentDateTime()
        self.setSelectedDate(current_datetime.date())
        self.datetime_edit.setDateTime(current_datetime)  # 更新 QDateTimeEdit 的值

    def showEvent(self, event):
        """重写 showEvent 方法，监听日历的显示事件"""
        # 获取当前选中的日期
        current_date = self.selectedDate()

        # 检查日期是否小于 1970 年 1 月 1 日
        if current_date < QDate(1970, 1, 1):
            # 将日期设置为今天的日期
            today = QDate.currentDate()
            self.setSelectedDate(today)

        # 调用父类的 showEvent 方法
        super().showEvent(event)


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
