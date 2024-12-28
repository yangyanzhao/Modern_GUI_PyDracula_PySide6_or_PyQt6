import random
import sys

from PySide6 import QtAsyncio
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QWidget, QSpacerItem, QSizePolicy, \
    QPushButton, QVBoxLayout, QLineEdit, QApplication

from widgets.cocos_widgets.c_pagination_bar import CPaginationBar, PaginationStyle


class DemoWindow(QWidget):

    def __init__(self, *args, **kwargs):
        super(DemoWindow, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(self)

        # 分页控件
        self.paginationBar1 = CPaginationBar(self, totalPages=20)
        # 设置扁平样式
        self.paginationBar1.pageChanged.connect(lambda page: print(f"当前页{page}"))
        layout.addWidget(self.paginationBar1)
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum))

        # 分页控件
        self.paginationBar2 = CPaginationBar(self, totalPages=20)
        # 设置普通样式
        self.paginationBar2.setStyleSheet(PaginationStyle)
        self.paginationBar2.pageChanged.connect(lambda page: print(f"当前页{page}"))
        layout.addWidget(self.paginationBar2)
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum))

        # 分页控件
        self.paginationBar3 = CPaginationBar(self, totalPages=20)
        # 设置信息
        self.paginationBar3.setInfos('共 400 条')
        self.paginationBar3.pageChanged.connect(lambda page: print(f"当前页{page}"))
        layout.addWidget(self.paginationBar3)
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum))

        # 分页控件
        self.paginationBar4 = CPaginationBar(self, totalPages=20)
        # 设置信息
        self.paginationBar4.setInfos('共 400 条')
        # 开启跳转功能
        self.paginationBar4.setJumpWidget(True)
        # 设置普通样式
        self.paginationBar4.setStyleSheet(PaginationStyle)
        self.paginationBar4.pageChanged.connect(lambda page: print(f"当前页{page}"))
        layout.addWidget(self.paginationBar4)
        layout.addItem(QSpacerItem(40, 40, QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.pageEdit = QLineEdit(self)
        self.pageEdit.setValidator(QIntValidator(self.pageEdit))
        self.pageEdit.setPlaceholderText('输入总页数')
        layout.addWidget(self.pageEdit)
        self.setButton = QPushButton('设置总页数', self, clicked=self.doSetPageNumber)
        layout.addWidget(self.setButton)

    def doSetPageNumber(self):
        page = self.pageEdit.text().strip()
        if not page:
            page = random.randint(0,10)
        page = int(page)
        self.paginationBar1.setTotalPages(page)
        self.paginationBar2.setTotalPages(page)
        self.paginationBar3.setTotalPages(page)
        self.paginationBar4.setTotalPages(page)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWindow()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
