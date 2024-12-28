import sys

from PySide6 import QtAsyncio

from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication

from widgets.cocos_widgets.c_marquee_label import AnimatedLabel, MarqueeLabel, DynamicTimeLabel, CombinedLabel


class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.animated_label = AnimatedLabel("反弹！")
        self.animated_label.start_animation()
        layout.addWidget(self.animated_label)

        self.marquee_label = MarqueeLabel("跑马灯",speed=10)
        layout.addWidget(self.marquee_label)

        self.dynamic_time_label = DynamicTimeLabel()
        layout.addWidget(self.dynamic_time_label)

        self.combined_label = CombinedLabel()
        layout.addWidget(self.combined_label)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWindow()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
