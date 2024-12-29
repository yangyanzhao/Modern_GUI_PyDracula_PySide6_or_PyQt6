import os
import sys
import tempfile

from PySide6 import QtAsyncio
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QMenu, QFileDialog, QVBoxLayout, QApplication
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtCore import QUrl, Qt, QTimer
from PySide6.QtGui import QColor, QPalette

from framework.widgets.cocos_widgets.c_voice_message.icons import icons
from framework.widgets.dayu_widgets import MBadge, MToolButton
from framework.widgets.dayu_widgets.qt import MIcon
from mutagen.mp3 import MP3


class CVoiceMessage(QWidget):
    def __init__(self, audio_data, alignment=Qt.AlignRight, has_dot=False, parent=None):
        super().__init__(parent)
        self.volume_icons = [
            MIcon(icons["volume-low.svg"], color='black'),
            MIcon(icons["volume-medium.svg"], color='black'),
            MIcon(icons["volume-high.svg"], color='black')
        ]
        self.volume_icons_current_index = 2
        self.audio_data = audio_data  # 二进制音频数据
        self.alignment = alignment
        self.has_dot = has_dot
        # 创建临时文件保存音频
        self.audio_file = self.save_audio_to_temp_file(audio_data)
        self.is_played = False
        self.player = QMediaPlayer()
        # 设置媒体内容
        self.player.setSource(QUrl.fromLocalFile(self.audio_file))
        self.timer = QTimer(self)
        self.timer.setInterval(500)  # 500ms 检查播放状态
        self.setContentsMargins(0, 0, 0, 0)

        # 自动检测音频时长
        self.duration = self.get_audio_duration(self.audio_file)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.center_widget = QWidget()
        self.center_widget.setContentsMargins(0, 0, 0, 0)
        self.center_widget.setStyleSheet(
            """
            QLabel {
            background-color: #95EC69;
            border-top-left-radius: 5px;
            border-top-right-radius: 0px;
            border-bottom-left-radius: 5px;
            border-bottom-right-radius: 0px;
            padding: 10px;
            color: #000000;
            }
            MToolButton {
            background-color: #95EC69;
            border-top-left-radius: 0px;
            border-top-right-radius: 5px;
            border-bottom-left-radius: 0px;
            border-bottom-right-radius: 5px;
            padding: 10px;
            color: #000000;
            }
            QLabel:hover,MToolButton:hover {
                background-color: #89D961; /* 鼠标悬停时的背景色 */
            }
            """
            if alignment == Qt.AlignRight
            else
            """
            QLabel,MToolButton {
            background-color: #FFFFFF; 
            border-top-left-radius: 0px;
            border-top-right-radius: 5px;
            border-bottom-left-radius: 0px;
            border-bottom-right-radius: 5px;
            padding: 10px;
            color: #000000;
            }
            MToolButton {
            background-color: #FFFFFF;
            border-top-left-radius: 5px;
            border-top-right-radius: 0px;
            border-bottom-left-radius: 5px;
            border-bottom-right-radius: 0px;
            padding: 10px;
            color: #000000;
            }
            QLabel:hover,MToolButton:hover {
                background-color: #EBEBEB; /* 鼠标悬停时的背景色 */
            }
            """
        )

        layout.addWidget(self.center_widget)
        center_layout = QHBoxLayout(self.center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        # 创建界面元素
        self.tool_button = MToolButton()
        self.tool_button.setFixedWidth(52)
        self.tool_button.setIcon(self.volume_icons[self.volume_icons_current_index])
        self.tool_button.clicked.connect(self.play_audio)
        # 播放状态
        if self.alignment == Qt.AlignLeft:
            self.status_label = QLabel(f"{self.duration}\"")
            self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        else:
            self.status_label = QLabel(f"{self.duration}\"")
            self.status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # 动态调整宽度，最小100，最长400
        self.center_widget.setFixedWidth(min(150 + self.duration * 5, 400))
        self.center_widget.setFixedHeight(52)  # 高度固定
        if alignment == Qt.AlignLeft:
            center_layout.addWidget(self.tool_button)
            center_layout.addWidget(self.status_label)
            if has_dot:
                self.badge_dot = MBadge.dot(show=True, widget=self.status_label, )  # 小圆点
                center_layout.addWidget(self.badge_dot)
        else:
            center_layout.addWidget(self.status_label)
            if has_dot:
                self.badge_dot = MBadge.dot(show=True, widget=self.status_label)  # 小圆点
                center_layout.addWidget(self.badge_dot)
            center_layout.addWidget(self.tool_button)

        # 绑定点击事件
        self.center_widget.mousePressEvent = self.play_audio

        # 右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # 监听播放完成事件
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)

        # 定时器检测播放状态
        self.timer.timeout.connect(self.update_playing_status)

    def get_audio_duration(self, audio_file):
        try:
            audio = MP3(audio_file)
            return int(audio.info.length)
        except Exception as e:
            print(f"无法读取音频时长: {e}")
            return 0

    def save_audio_to_temp_file(self, audio_data):
        with open(audio_data, 'rb') as f:
            audio_bytes = f.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file.write(audio_bytes)
            return temp_file.name

    def play_audio(self, event):
        print("开始播放音频")
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.player.setSource(QUrl.fromLocalFile(self.audio_file))
            if self.is_played:
                self.is_played = False
            if self.alignment == Qt.AlignLeft:
                self.status_label.setText(f"{self.duration}\"   暂停")
            else:
                self.status_label.setText(f"暂停   {self.duration}\"")
            self.timer.stop()  # 启动定时器

        else:
            if self.has_dot:
                self.badge_dot.set_dayu_dot(False)
            self.player.setSource(QUrl.fromLocalFile(self.audio_file))
            self.player.play()
            if not self.is_played:
                self.is_played = True
            if self.alignment == Qt.AlignLeft:
                self.status_label.setText(f"{self.duration}\"   正在播放..")
            else:
                self.status_label.setText(f"正在播放..   {self.duration}\"")
            self.timer.start()  # 启动定时器

    def on_media_status_changed(self, status):
        """监听媒体状态变化"""
        print(status)
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.status_label.setText(f"{self.duration}\"")
            self.timer.stop()  # 停止定时器
            print("播放完成")
    def update_playing_status(self):
        # 播放过程中保持“正在播放”状态
        if self.has_dot:
            self.badge_dot.set_dayu_dot(False)
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            if self.alignment == Qt.AlignLeft:
                self.status_label.setText(f"{self.duration}\"   正在播放..")
            else:
                self.status_label.setText(f"正在播放..   {self.duration}\"")
            self.tool_button.setIcon(MIcon("24gl-volumeMiddle.svg"))
            self.volume_icons_current_index += 1
            if self.volume_icons_current_index >= len(self.volume_icons):
                self.volume_icons_current_index = 0
            self.tool_button.setIcon(self.volume_icons[self.volume_icons_current_index])
            print("播放中")

    def show_context_menu(self, pos):
        menu = QMenu(self)
        save_action = menu.addAction("打开文件存放地")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == save_action:
            self.save_audio_file()

    def save_audio_file(self):
        # file_dialog = QFileDialog(self)
        # file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        # file_dialog.setDefaultSuffix("mp3")
        # file_dialog.setNameFilter("MP3 files (*.mp3)")
        file_path, _ = QFileDialog.getSaveFileName(self, "保存音频", os.path.basename(self.audio_file),
                                                   "MP3 files (*.mp3)")
        if file_path:
            with open(self.audio_file, "rb") as f_in, open(file_path, "wb") as f_out:
                f_out.write(f_in.read())

    def set_bg_color(self, color):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setAutoFillBackground(True)
        self.setPalette(palette)


class DemoWidget(QWidget):
    def __init__(self):
        super(DemoWidget, self).__init__()
        self.setWindowTitle("Demo")
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        c_voice_message_widget_right = CVoiceMessage(audio_data='12月20日.MP3', alignment=Qt.AlignRight,
                                                           has_dot=True)
        c_voice_message_widget_left = CVoiceMessage(audio_data='12月20日.MP3', alignment=Qt.AlignLeft,
                                                          has_dot=True)

        layout.addWidget(c_voice_message_widget_right)
        layout.addWidget(c_voice_message_widget_left)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    demo_widget = DemoWidget()
    # 显示窗口
    demo_widget.show()

    QtAsyncio.run(handle_sigint=True)
