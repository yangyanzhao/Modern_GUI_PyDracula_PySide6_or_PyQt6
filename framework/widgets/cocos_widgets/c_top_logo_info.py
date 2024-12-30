import asyncio
import logging

from PySide6.QtCore import QSize, QRect, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QLabel, QApplication
from qasync import QEventLoop

from resources.framework.images import images


class CTopLogoInfo(QFrame):
    def __init__(self, height=50, parent=None):
        """
        LOGO控件
        :param height: 固定高度
        :param parent:
        """
        super(CTopLogoInfo, self).__init__(parent=parent)
        # LOGO信息
        self.setObjectName(u"topLogoInfo")
        self.setFixedHeight(height)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setContentsMargins(0, 0, 0, 0)

        # LOGO图标
        self.topLogo = QFrame(self)
        self.topLogo.setObjectName(u"topLogo")
        self.topLogo.setGeometry(QRect(10, 5, 42, 42))
        self.topLogo.setMinimumSize(QSize(42, 42))
        self.topLogo.setMaximumSize(QSize(42, 42))
        self.topLogo.setFrameShape(QFrame.Shape.NoFrame)
        self.topLogo.setFrameShadow(QFrame.Shadow.Raised)

        right_slash = '\\'
        self.topLogo.setStyleSheet(
            rf"""
            background-image: url({images['PyDracula.png'].replace(right_slash, '/')});
            background-color: rgb(33, 37, 43);
            background-position: centered;
            background-repeat: no-repeat;
            """)
        # LOGO文字标题
        self.titleLeftApp = QLabel(self)
        self.titleLeftApp.setText("PyDracula")
        self.titleLeftApp.setObjectName(u"titleLeftApp")
        self.titleLeftApp.setGeometry(QRect(70, 8, 160, 20))
        font1 = QFont()
        font1.setFamily(u"Segoe UI Semibold")
        font1.setPointSize(12)
        font1.setBold(False)
        font1.setItalic(False)
        self.titleLeftApp.setFont(font1)
        self.titleLeftApp.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)
        self.titleLeftApp.setStyleSheet(
            rf"""
            font: 63 12pt "Segoe UI Semibold";color: rgb(128,128,115);
            """
        )

        # LOGO文字描述
        self.titleLeftDescription = QLabel(self)
        self.titleLeftDescription.setText("Modern GUI / Flat Style")
        self.titleLeftDescription.setObjectName(u"titleLeftDescription")
        self.titleLeftDescription.setGeometry(QRect(70, 27, 160, 16))
        font2 = QFont()
        font2.setFamily(u"Segoe UI")
        font2.setPointSize(8)
        font2.setBold(False)
        font2.setItalic(False)
        self.titleLeftDescription.setFont(font2)
        self.titleLeftDescription.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)
        self.titleLeftDescription.setStyleSheet(
            rf"""
            font: 8pt "Segoe UI"; color: rgb(189, 147, 249);
            """
        )


if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = CTopLogoInfo()
    # 显示窗口
    demo_widget.show()
    with loop:
        loop.run_forever()
