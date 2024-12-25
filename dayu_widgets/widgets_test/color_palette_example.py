import sys

from PySide6 import QtAsyncio
from PySide6.QtWidgets import QApplication

from dayu_widgets import MTheme
from dayu_widgets.color_palette import MColorPaletteDialog

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = MColorPaletteDialog(init_color="#1890ff")
    MTheme().apply(demo_widget)
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
