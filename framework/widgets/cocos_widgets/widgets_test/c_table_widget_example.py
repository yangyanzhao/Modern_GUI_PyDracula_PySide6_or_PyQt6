import sys
from PySide6 import QtAsyncio, QtWidgets
from PySide6.QtWidgets import QWidget, QApplication, QTableWidgetItem
from framework.widgets.cocos_widgets.c_table_widget.c_table_widget import CTableWidget


class DemoWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(500, 500)
        layout = QtWidgets.QVBoxLayout(self)

        self.table_widget = CTableWidget()
        # 设置表格的行数和列数
        self.table_widget.setRowCount(5)
        self.table_widget.setColumnCount(3)

        # 设置表头标签
        self.table_widget.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])

        # 填充表格数据
        for i in range(5):
            for j in range(3):
                self.table_widget.setItem(i, j, QTableWidgetItem(f"Item {i},{j}"))

        # 将表格添加到布局中
        layout.addWidget(self.table_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWindow()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
