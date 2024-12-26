import asyncio
import sys

from PySide6 import QtAsyncio
from PySide6.QtCore import QEvent, QTimer, QPropertyAnimation, QEasingCurve, QAbstractAnimation, QSize
from PySide6.QtGui import Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QApplication, QHBoxLayout, QWidget, QLabel

from cocos_widgets.c_dialog import icons
from cocos_widgets.c_dialog.frameless_dialog_abstract import FramelessDialogAbstract
from dayu_widgets import MLabel, MPushButton
from dayu_widgets.qt import MPixmap
from PySide6.QtWidgets import QVBoxLayout


class CConfirmDialog(FramelessDialogAbstract):
    def __init__(self, title, content, parent, is_mask=True, background_color=None, font_color=None,
                 icon: QSvgWidget = None,
                 width=None):
        super().__init__(has_title_bar=True, parent=parent)
        self.is_mask = is_mask
        self.setWindowTitle(title)
        if width is not None:
            self.setMinimumWidth(width)
        self.setModal(True)  # 确保对话框是模态的
        if is_mask:
            # 创建遮罩层
            self.mask_widget = QWidget(parent)
            self.mask_widget.setStyleSheet("background-color: rgba(0, 0, 0, 100);")

            self.mask_widget.resize(parent.size())
            self.mask_widget.hide()
            # 显示遮罩层
            self.mask_widget.resize(parent.size())
            self.mask_widget.show()
        # 安装事件过滤器
        parent.installEventFilter(self)

        # 创建布局
        q_widget = QWidget()
        q_widget.setObjectName("q_widget")
        layout = QVBoxLayout(q_widget)
        style = f"""
                                QWidget#q_widget,QLabel,QSvgWidget {{
                                    border-top-left-radius: 10px;
                                    border-top-right-radius: 10px;
                                    border-bottom-left-radius: 10px;
                                    border-bottom-right-radius: 10px;
                                    background-color: '{background_color}';
                                }}
                                """ if background_color else f"""
                                QWidget#q_widget,QLabel,QSvgWidget {{
                                    border-top-left-radius: 10px;
                                    border-top-right-radius: 10px;
                                    border-bottom-left-radius: 10px;
                                    border-bottom-right-radius: 10px;
                                }}
                                """
        q_widget.setStyleSheet(style)
        h_layout = QHBoxLayout()
        # 标题
        self.label = MLabel(f"<h2>{title}</h2>")
        layout.addWidget(self.label)
        # 图标
        if icon is not None:
            h_layout.addWidget(icon)
        # 内容
        if font_color:
            self.label = MLabel(f"<h4 style='color:{font_color};'>{content}</h4>")
        else:
            self.label = MLabel(f"<h4>{content}</h4>")
        self.label.setWordWrap(True)
        h_layout.addWidget(self.label)
        layout.addLayout(h_layout)
        # 两个按钮
        self.button_ok = MPushButton("OK")
        self.button_cancel = MPushButton("Cancel")
        qh_box_layout = QHBoxLayout()
        qh_box_layout.addWidget(self.button_ok)
        qh_box_layout.addWidget(self.button_cancel)
        layout.addLayout(qh_box_layout)

        # 连接按钮的点击事件
        self.button_ok.clicked.connect(self.accept)
        self.button_ok.clicked.connect(self.close)
        self.button_cancel.clicked.connect(self.reject)
        self.button_cancel.clicked.connect(self.close)

        # 添加到中心布局
        self.center_layout.addWidget(q_widget)

    def eventFilter(self, obj, event):
        """
        遮罩层跟着窗口大小进行缩放
        """
        if obj == self.parent and event.type() == QEvent.Resize:
            # 调整遮罩层大小
            if self.is_mask:
                self.mask_widget.resize(self.parent.size())
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        # 隐藏遮罩层
        if self.is_mask:
            self.mask_widget.hide()
        super().closeEvent(event)

    @staticmethod
    def error(title, content, parent, is_mask=True):
        svg_widget = QSvgWidget(icons['操作失败.svg'])
        svg_widget.setFixedSize(QSize(16, 16))
        widget = CConfirmDialog(title=title, content=content, parent=parent, is_mask=is_mask,
                                background_color='#2B2121',
                                font_color='#C23E45', icon=svg_widget)
        widget.setModal(True)
        exec_ = widget.exec_()

    @staticmethod
    def success(title, content, parent, is_mask=True):
        svg_widget = QSvgWidget(icons['操作成功.svg'])
        svg_widget.setFixedSize(QSize(16, 16))
        widget = CConfirmDialog(title=title, content=content, parent=parent, is_mask=is_mask,
                                background_color='#1D241A',
                                font_color='#67C23A',
                                icon=svg_widget)
        widget.setModal(True)
        return widget

    @staticmethod
    def message(title, content, parent, is_mask=True):
        svg_widget = QSvgWidget(icons['操作信息.svg'])
        svg_widget.setFixedSize(QSize(16, 16))
        widget = CConfirmDialog(title=title, content=content, parent=parent, is_mask=is_mask, icon=svg_widget)
        widget.setModal(True)
        return widget

    @staticmethod
    def warning(title, content, parent, is_mask=True):
        svg_widget = QSvgWidget(icons['操作警告.svg'])
        svg_widget.setFixedSize(QSize(16, 16))
        widget = CConfirmDialog(title=title, content=content, parent=parent, is_mask=is_mask,
                                background_color='#252019',
                                font_color='#E6A23C', icon=svg_widget)
        widget.setModal(True)
        return widget

    @staticmethod
    def danger(title, content, parent, is_mask=True):
        svg_widget = QSvgWidget(icons['操作危险.svg'])
        svg_widget.setFixedSize(QSize(16, 16))
        widget = CConfirmDialog(title=title, content=content, parent=parent, is_mask=is_mask,
                                background_color='#2B2121',
                                font_color='#FF0000',
                                icon=svg_widget)
        widget.setModal(True)
        return widget


class CMessageDialog(FramelessDialogAbstract):
    def __init__(self, content, parent, duration=3000, is_mask=True, background_color=None, font_color=None,
                 icon: QSvgWidget = None,
                 width=None):
        super().__init__(has_title_bar=True, has_max_btn=False, has_min_btn=False, has_close_btn=True,
                         parent=parent)
        self.is_mask = is_mask
        if width is not None:
            self.setMinimumWidth(width)
        self.setModal(True)  # 确保对话框是模态的
        if is_mask:
            # 创建遮罩层
            self.mask_widget = QWidget(parent)
            self.mask_widget.setStyleSheet("background-color: rgba(0, 0, 0, 100);")

            self.mask_widget.resize(parent.size())
            self.mask_widget.hide()
            # 显示遮罩层
            self.mask_widget.resize(parent.size())
            self.mask_widget.show()
        # 安装事件过滤器
        parent.installEventFilter(self)

        # 创建布局
        q_widget = QWidget()
        layout = QHBoxLayout(q_widget)
        style = f"""
                        QWidget {{
                            border-top-left-radius: 10px;
                            border-top-right-radius: 10px;
                            border-bottom-left-radius: 10px;
                            border-bottom-right-radius: 10px;
                            background-color: '{background_color}';
                        }}
                        """ if background_color else f"""
                        QWidget {{
                            border-top-left-radius: 10px;
                            border-top-right-radius: 10px;
                            border-bottom-left-radius: 10px;
                            border-bottom-right-radius: 10px;
                        }}
                        """
        q_widget.setStyleSheet(style)
        # 图标
        if icon is not None:
            layout.addWidget(icon)
        # 内容
        if font_color:
            self.label = MLabel(f"<h4 style='color:{font_color};'>{content}</h4>")
        else:
            self.label = MLabel(f"<h4>{content}</h4>")
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        # 添加到中心布局
        self.center_layout.addWidget(q_widget)

        _close_timer = QTimer(self)
        _close_timer.setSingleShot(True)
        _close_timer.timeout.connect(lambda: self.close())
        _close_timer.setInterval(duration)
        _close_timer.start()

    def eventFilter(self, obj, event):
        """
        遮罩层跟着窗口大小进行缩放
        """
        if obj == self.parent and event.type() == QEvent.Resize:
            # 调整遮罩层大小
            if self.is_mask:
                self.mask_widget.resize(self.parent.size())
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        # 隐藏遮罩层
        if self.is_mask:
            self.mask_widget.hide()
        super().closeEvent(event)

    @staticmethod
    def error(content, parent, duration=3000, is_mask=False):
        svg_widget = QSvgWidget(icons['操作失败.svg'])
        svg_widget.setFixedSize(QSize(16, 16))
        widget = CMessageDialog(content=content, parent=parent, duration=duration, is_mask=is_mask,
                                background_color='#2B2121',
                                font_color='#C23E45', icon=svg_widget)
        widget.setModal(True)
        exec_ = widget.exec()

    @staticmethod
    def success(content, parent, duration=3000, is_mask=False):
        svg_widget = QSvgWidget(icons['操作成功.svg'])
        svg_widget.setFixedSize(QSize(16, 16))
        widget = CMessageDialog(content=content, parent=parent, duration=duration, is_mask=is_mask,
                                background_color='#1D241A',
                                font_color='#67C23A',
                                icon=svg_widget)
        widget.setModal(True)
        exec_ = widget.exec()

    @staticmethod
    def message(content, parent, duration=3000, is_mask=False):
        svg_widget = QSvgWidget(icons['操作信息.svg'])
        svg_widget.setFixedSize(QSize(16, 16))
        widget = CMessageDialog(content=content, parent=parent, duration=duration, is_mask=is_mask, icon=svg_widget)
        widget.setModal(True)
        exec_ = widget.exec()

    @staticmethod
    def warning(content, parent, duration=3000, is_mask=False):
        svg_widget = QSvgWidget(icons['操作警告.svg'])
        svg_widget.setFixedSize(QSize(16, 16))
        widget = CMessageDialog(content=content, parent=parent, duration=duration, is_mask=is_mask,
                                background_color='#252019',
                                font_color='#E6A23C', icon=svg_widget)
        widget.setModal(True)
        exec_ = widget.exec()

    @staticmethod
    def danger(content, parent, duration=3000, is_mask=False):
        svg_widget = QSvgWidget(icons['操作危险.svg'])
        svg_widget.setFixedSize(QSize(16, 16))
        widget = CMessageDialog(content=content, parent=parent, duration=duration, is_mask=is_mask,
                                background_color='#2B2121',
                                font_color='#FF0000',
                                icon=svg_widget)
        widget.setModal(True)
        exec_ = widget.exec()


class DemoWidget(QWidget):
    def __init__(self):
        super(DemoWidget, self).__init__()
        layout = QVBoxLayout(self)
        button0 = MPushButton("错误")
        button0.clicked.connect(lambda: CMessageDialog.error(content="这是一条消息通知", parent=self, duration=15000))
        layout.addWidget(button0)

        button1 = MPushButton("成功")
        button1.clicked.connect(lambda: CMessageDialog.success(content="这是一条消息通知", parent=self, duration=15000))
        layout.addWidget(button1)

        button2 = MPushButton("消息")
        button2.clicked.connect(lambda: CMessageDialog.message(content="这是一条消息通知", parent=self, duration=15000))
        layout.addWidget(button2)

        button3 = MPushButton("警告")
        button3.clicked.connect(lambda: CMessageDialog.warning(content="这是一条消息通知", parent=self, duration=15000))
        layout.addWidget(button3)

        button4 = MPushButton("危险")
        button4.clicked.connect(lambda: CMessageDialog.danger(
            content="第一组短对话开始前和最后一组短对话结束后都要停顿每组短对话时间间隔的一半", parent=self,
            duration=15000))
        layout.addWidget(button4)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
