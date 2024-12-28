import sys

from PySide6 import QtWidgets
from PySide6.QtCore import QStringListModel, Qt
from PySide6.QtWidgets import QLineEdit, QCompleter

from framework.widgets.dayu_widgets.completer import MCompleter

if __name__ == "__main__":
    # 创建应用程序
    app = QtWidgets.QApplication(sys.argv)

    # 创建主窗口
    window = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(window)

    # 创建一个 QLineEdit 作为输入框
    line_edit = QLineEdit(window)
    layout.addWidget(line_edit)

    # 创建一个 QCompleter 并设置模型
    completer_model = QStringListModel(["Apple", "Append", "Banana", "Cherry", "Date", "Elderberry"])
    completer = MCompleter(parent=line_edit)
    completer.setModel(completer_model)
    completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)  # 弹出补全列表
    completer.setCaseSensitivity(Qt.CaseInsensitive)  # 忽略大小写
    completer.popup().setStyleSheet("background-color: lightgreen; color: black;")  # 窗口的样式
    completer.setFilterMode(Qt.MatchContains)  # 匹配模式

    # 将 QCompleter 绑定到 QLineEdit
    line_edit.setCompleter(completer)

    # 显示窗口
    window.show()

    # 运行应用程序
    sys.exit(app.exec())
