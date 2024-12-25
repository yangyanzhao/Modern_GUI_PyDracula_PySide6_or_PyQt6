import asyncio
import sys

from PySide6 import QtAsyncio
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton, QTextEdit, QHBoxLayout

from dayu_widgets import dayu_theme, MLoadingWrapper, MTheme, MLoading


class DemoWidget(QWidget):
    def __init__(self, parent=None):
        super(DemoWidget, self).__init__(parent)
        self.setWindowTitle("MLoading控件学习")
        # 布局
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        huge_loading = MLoading.huge(color='red')  # 创建巨大的加载动画
        large_loading = MLoading.large()  # 创建大的加载动画
        medium_loading = MLoading.medium()  # 创建中等大小的加载动画
        small_loading = MLoading.small()  # 创建小的加载动画
        tiny_loading = MLoading.tiny()  # 创建极小的加载动画
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(huge_loading)
        self.h_layout.addWidget(large_loading)
        self.h_layout.addWidget(medium_loading)
        self.h_layout.addWidget(small_loading)
        self.h_layout.addWidget(tiny_loading)
        self.main_layout.addLayout(self.h_layout)

        # 添加一个查询按钮
        self.button = QPushButton("查询数据", self)
        # 点击按钮，触发加载包装器的加载状态
        self.button.clicked.connect(lambda: asyncio.ensure_future(self.btn_handle()))
        self.main_layout.addWidget(self.button)

        # 添加一个文本框用来显示加载的数据
        self.text_edit = QTextEdit(self)
        self.main_layout.addWidget(self.text_edit)

        # 使用MLoadingWrapper加载包装器来包裹住文本框
        self.loading_wrapper = MLoadingWrapper(widget=self.text_edit, loading=False, size=64, color=dayu_theme.red)
        self.main_layout.addWidget(self.loading_wrapper)

    async def btn_handle(self):
        # 开启加载
        self.loading_wrapper.set_dayu_loading(True)
        # 模拟查询耗时1秒
        await asyncio.sleep(1)
        # 结束加载
        self.loading_wrapper.set_dayu_loading(False)
        # 渲染数据
        self.text_edit.setText(
            "陌生人并不在意你的梦想是什么，"
            "他们寻求满足自己的需要和欲望。"
            "在你介入没有明确需求、品牌或目的的生意时，"
            "风险将会累积。"
            "当你去做一项自己喜欢而不是需要去做的生意时，风险在累积。" * 2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    MTheme().apply(demo_widget)
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
