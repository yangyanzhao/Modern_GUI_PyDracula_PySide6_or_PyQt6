from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtWidgets import QWidget, QTextEdit, QPushButton, QVBoxLayout, QApplication


class PrintApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PySide6 Print Example")

        # 创建一个 QTextEdit 用于输入文本
        self.text_edit = QTextEdit(self)

        # 创建一个按钮用于触发打印
        self.print_button = QPushButton("Print", self)
        self.print_button.clicked.connect(self.print_document)

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.print_button)
        self.setLayout(layout)

    def print_document(self):
        # 创建一个 QPrinter 对象
        printer = QPrinter(QPrinter.HighResolution)

        # 创建一个打印对话框
        print_dialog = QPrintDialog(printer, self)

        # 如果用户点击了打印对话框的“打印”按钮
        if print_dialog.exec() == QPrintDialog.Accepted:
            # 将 QTextEdit 的内容打印到打印机
            self.text_edit.document().print_(printer)


if __name__ == "__main__":
    app = QApplication([])

    window = PrintApp()
    window.show()

    app.exec()
