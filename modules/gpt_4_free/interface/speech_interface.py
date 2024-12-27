import asyncio
import logging
import time
import traceback

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QSplitter,
    QSizePolicy, QLabel
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize

from cocos_widgets.c_avatar import CAvatar
from cocos_widgets.c_dialog.c_confirm_dialog import CConfirmDialog
from cocos_widgets.c_splash_screen.c_splash_screen import increase_counter
from cocos_widgets.c_voice_message.c_voice_message import CVoiceMessageWidget
from dayu_widgets import MFieldMixin, MTheme, MTextEdit, MPushButton, MLabel, MComboBox, MMenu
from qasync import QEventLoop

from db.mysql.async_utils import is_in_async_context
from modules.gpt_4_free.api.hailuo.hailuo_free_api_four import HailuoAPIFour
from modules.gpt_4_free.api.hailuo.hailuo_free_api_one import HailuoAPIOne
from modules.gpt_4_free.api.hailuo.hailuo_free_api_three import HailuoAPIThree
from modules.gpt_4_free.api.hailuo.hailuo_free_api_two import HailuoAPITwo
from modules.gpt_4_free.icons import icons
from utils.position_util import find_all_parent_widgets

# 大模型映射
llm_mapping = {
    "hailuo-one": HailuoAPIOne,
    "hailuo-two": HailuoAPITwo,
    "hailuo-three": HailuoAPIThree,
    "hailuo-four": HailuoAPIFour,
}
# 大模型菜单
llm_menu_list = [
    {
        "label": "Hailuo",
        "children": [
            {
                "label": "hailuo-one",
                "value": "hailuo-one"
            },
            {
                "label": "hailuo-two",
                "value": "hailuo-two"
            },
            {
                "label": "hailuo-three",
                "value": "hailuo-three"
            },
            {
                "label": "hailuo-four",
                "value": "hailuo-four"
            },
        ]
    },
]
voice_menu_list = [
    {"label": "思远", "value": "male-botong"},
    {"label": "心悦", "value": "Podcast_girl"},
    {"label": "子轩", "value": "boyan_new_hailuo"},
    {"label": "灵儿", "value": "female-shaonv"},
    {"label": "语嫣", "value": "YaeMiko_hailuo"},
    {"label": "少泽", "value": "xiaoyi_mix_hailuo"},
    {"label": "芷溪", "value": "xiaomo_sft"},
    {"label": "浩翔(英文)", "value": "cove_test2_hailuo"},
    {"label": "雅涵(英文)", "value": "scarlett_hailuo"},
    {"label": "模仿雷电将军", "value": "Leishen2_hailuo"},
    {"label": "模仿钟离", "value": "Zhongli_hailuo"},
    {"label": "模仿派蒙", "value": "Paimeng_hailuo"},
    {"label": "模仿可莉", "value": "keli_hailuo"},
    {"label": "模仿胡桃", "value": "Hutao_hailuo"},
    {"label": "模仿熊二", "value": "Xionger_hailuo"},
    {"label": "模仿海绵宝宝", "value": "Haimian_hailuo"},
    {"label": "模仿变形金刚", "value": "Robot_hunter_hailuo"},
    {"label": "小玲玲", "value": "Linzhiling_hailuo"},
    {"label": "拽妃", "value": "huafei_hailuo"},
    {"label": "东北er", "value": "lingfeng_hailuo"},
    {"label": "老铁", "value": "male_dongbei_hailuo"},
    {"label": "北京er", "value": "Beijing_hailuo"},
    {"label": "JayJay", "value": "JayChou_hailuo"},
    {"label": "潇然", "value": "Daniel_hailuo"},
    {"label": "沉韵", "value": "Bingjiao_zongcai_hailuo"},
    {"label": "瑶瑶", "value": "female-yaoyao-hd"},
    {"label": "晨曦", "value": "murong_sft"},
    {"label": "沐珊", "value": "shangshen_sft"},
    {"label": "祁辰", "value": "kongchen_sft"},
    {"label": "夏洛特", "value": "shenteng2_hailuo"},
    {"label": "郭嘚嘚", "value": "Guodegang_hailuo"},
    {"label": "小月月", "value": "yueyue_hailuo"},
]


class CustomTextEdit(MTextEdit):
    returnPressed = Signal()  # 定义一个信号

    def keyPressEvent(self, event):
        # 检查是否按下了 Enter 键
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # 检查是否同时按下了 Shift 键
            if event.modifiers() & Qt.ShiftModifier:
                # 插入换行符
                self.textCursor().insertText("\n")
            else:
                self.returnPressed.emit()
                # 阻止默认的 Enter 键行为（插入新段落）
                event.ignore()
        else:
            # 其他按键事件正常处理
            super().keyPressEvent(event)


class SpeechInterface(QWidget, MFieldMixin):
    def __init__(self, parent=None):
        increase_counter("GPT语音初始化...")
        super().__init__(parent)
        self.setWindowTitle("仿微信聊天界面")
        self.set_center_layout = QVBoxLayout(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.set_center_layout.setSpacing(0)
        # 主窗口的中央小部件
        central_widget = QWidget()
        self.set_center_layout.addWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # 使用 QSplitter 实现可调节布局
        self.splitter = QSplitter(Qt.Vertical)
        self.layout.addWidget(self.splitter)

        # 消息显示区域
        self.chat_display_area = QScrollArea()

        self.chat_display_area.setStyleSheet("""
                    QScrollArea {
                        border: 0px solid #000000;  /* 设置边框样式 */
                    }
                    QWidget {
                        background-color: #3A3A3A;  /* 设置背景样式 */
                    }
                """)

        self.chat_display_area.setWidgetResizable(True)
        self.chat_display_widget = QWidget()
        self.chat_display_layout = QVBoxLayout(self.chat_display_widget)
        self.chat_display_layout.setAlignment(Qt.AlignTop)  # 消息从顶部开始排列
        self.chat_display_widget.setLayout(self.chat_display_layout)
        self.chat_display_area.setWidget(self.chat_display_widget)

        # 输入区域
        self.input_area = QWidget()
        self.input_layout = QHBoxLayout(self.input_area)
        self.llm_box = MComboBox()
        self.llm_box.set_formatter(lambda x: x[-1])  # 设置级联显示格式
        self.llm_box.setMaximumWidth(200)
        self.llm_box.setMinimumWidth(100)
        menu = MMenu(cascader=True, parent=self)
        menu.set_data(llm_menu_list)
        self.llm_box.set_menu(menu)

        self.voice_box = MComboBox()
        self.voice_box.set_formatter(lambda x: x[-1])  # 设置级联显示格式
        self.voice_box.setMaximumWidth(200)
        self.voice_box.setMinimumWidth(100)
        voice_menu = MMenu(cascader=True, parent=self)
        voice_menu.set_data(voice_menu_list)
        self.voice_box.set_menu(voice_menu)

        self.input_text = CustomTextEdit()
        self.input_text.returnPressed.connect(self.send_message)

        self.send_button = MPushButton("发送")
        self.send_button.clicked.connect(self.send_message)

        self.input_layout.addWidget(self.llm_box)
        self.input_layout.addWidget(self.voice_box)
        self.input_layout.addWidget(self.input_text)
        self.input_layout.addWidget(self.send_button)

        self.input_area.setLayout(self.input_layout)

        # 将显示区域和输入区域添加到 QSplitter 中
        self.splitter.addWidget(self.chat_display_area)
        self.splitter.addWidget(self.input_area)

        # 设置默认比例
        self.splitter.setStretchFactor(0, 99)
        self.splitter.setStretchFactor(1, 1)

    def send_message(self):
        # 获取输入框的文本
        message = self.input_text.toPlainText().strip()
        if message:
            # 显示在消息显示区域
            self.display_message(message, alignment=Qt.AlignRight)
            label_ing = MLabel("正在合成中...")
            self.display_label(label_ing, alignment=Qt.AlignLeft)
            self.input_text.clear()
            self.visitor_llm(message, label_ing)

    def visitor_llm(self, message, label_ing: QLabel):
        # 记录开始时间
        start_time = time.time()
        # 访问LLM API
        llm_select = self.llm_box.currentText()
        voice_select = self.voice_box.currentText()
        # 判断是否处于某个loop中
        if is_in_async_context():
            loop = asyncio.get_running_loop()
            # 当前loop是否正在运行
            if loop.is_running():
                result_future = asyncio.run_coroutine_threadsafe(
                    llm_mapping[llm_select].main_chat_audio_speech(message), loop)
                try:
                    # 设置超时时间
                    result = result_future.result(timeout=180)
                    # 记录结束时间
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    label_ing.setText(f"耗时: {elapsed_time:.3f} 秒")
                    self.display_images(result, alignment=Qt.AlignLeft)
                    return result
                except asyncio.TimeoutError:
                    logging.error("Task timed out after 180 seconds")
                    label_ing.setText("Task timed out after 180 seconds")
                except Exception as e:
                    logging.error(f"Task failed: {e}\n{traceback.format_exc()}")
                    label_ing.setText(f"Task failed: {e}\n{traceback.format_exc()}")
            else:
                result = loop.run_until_complete(llm_mapping[llm_select].main_chat_audio_speech(message, voice_select))
                # 记录结束时间
                end_time = time.time()
                elapsed_time = end_time - start_time
                label_ing.setText(f"耗时: {elapsed_time:.3f} 秒")
                self.display_images(result, alignment=Qt.AlignLeft)
                return result
        else:
            result = asyncio.run(llm_mapping[llm_select].main_chat_audio_speech(message, voice_select))
            # 记录结束时间
            end_time = time.time()
            elapsed_time = end_time - start_time
            label_ing.setText(f"耗时: {elapsed_time:.3f} 秒")
            self.display_images(result, alignment=Qt.AlignLeft)
            return result

    def display_message(self, message, alignment):
        # 创建一个标签用来显示消息
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        message_label.setStyleSheet(
            """
            QLabel {
            background-color: #95EC69;
            border-radius: 5px;
            padding: 10px;
            color: #000000;
            }
            QLabel:hover {
                background-color: #89D961; /* 鼠标悬停时的背景色 */
            }
            """
            if alignment == Qt.AlignRight
            else
            """
            QLabel {
            background-color: #FFFFFF; 
            border-radius: 5px;
            padding: 10px;
            color: #000000;
            }
            QLabel:hover {
                background-color: #EBEBEB; /* 鼠标悬停时的背景色 */
            }
            """
        )
        # 创建一个容器小部件，包含头像和消息标签
        message_container = QWidget()
        container_layout = QHBoxLayout(message_container)
        if alignment == Qt.AlignRight:
            container_layout.addStretch()
            avatar_right = CAvatar(shape=CAvatar.Circle, url=icons['avatar_m.jpeg'], size=CAvatar.SizeSmall)
            container_layout.addWidget(message_label)
            container_layout.addWidget(avatar_right)
        else:
            avatar_left = CAvatar(shape=CAvatar.Rectangle, url=icons['avatar_w.jpeg'], size=CAvatar.SizeSmall)
            container_layout.addWidget(avatar_left)
            container_layout.addWidget(message_label)
            container_layout.addStretch()
        container_layout.setContentsMargins(10, 5, 10, 5)
        self.chat_display_layout.addWidget(message_container)

        # 滚动到底部
        self.chat_display_area.verticalScrollBar().setValue(self.chat_display_area.verticalScrollBar().maximum())
        # 有时候滚动行为在画面刷新之前，导致没有滚动到底部，这里补一个延迟滚动。
        QTimer.singleShot(100, lambda: self.chat_display_area.verticalScrollBar().setValue(
            self.chat_display_area.verticalScrollBar().maximum()))

    def display_label(self, message_label, alignment):
        message_label.setWordWrap(True)
        message_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        message_label.setStyleSheet(
            """
            QLabel {
            background-color: #95EC69;
            border-radius: 5px;
            padding: 10px;
            color: #000000;
            }
            QLabel:hover {
                background-color: #89D961; /* 鼠标悬停时的背景色 */
            }
            """
            if alignment == Qt.AlignRight
            else
            """
            QLabel {
            background-color: #FFFFFF; 
            border-radius: 5px;
            padding: 10px;
            color: #000000;
            }
            QLabel:hover {
                background-color: #EBEBEB; /* 鼠标悬停时的背景色 */
            }
            """
        )
        # 创建一个容器小部件，包含头像和消息标签
        message_container = QWidget()
        container_layout = QHBoxLayout(message_container)
        if alignment == Qt.AlignRight:
            container_layout.addStretch()
            avatar_right = CAvatar(shape=CAvatar.Circle, url=icons['avatar_m.jpeg'], size=CAvatar.SizeSmall)
            container_layout.addWidget(message_label)
            container_layout.addWidget(avatar_right)
        else:
            avatar_left = CAvatar(shape=CAvatar.Rectangle, url=icons['avatar_w.jpeg'], size=CAvatar.SizeSmall)
            container_layout.addWidget(avatar_left)
            container_layout.addWidget(message_label)
            container_layout.addStretch()
        container_layout.setContentsMargins(10, 5, 10, 5)
        self.chat_display_layout.addWidget(message_container)

        # 滚动到底部
        self.chat_display_area.verticalScrollBar().setValue(self.chat_display_area.verticalScrollBar().maximum())
        # 有时候滚动行为在画面刷新之前，导致没有滚动到底部，这里补一个延迟滚动。
        QTimer.singleShot(100, lambda: self.chat_display_area.verticalScrollBar().setValue(
            self.chat_display_area.verticalScrollBar().maximum()))

    def display_images(self, voice, alignment):
        if voice is None:
            widgets = find_all_parent_widgets(self)
            widget = CConfirmDialog(title="生成失败",
                                    content="请查看日志",
                                    parent=widgets[-1])
            widget.setModal(True)
            exec_ = widget.exec_()
            return
        # 创建一个容器小部件，包含头像和语音标签
        message_container = QWidget()
        container_layout = QHBoxLayout(message_container)
        if alignment == Qt.AlignRight:
            container_layout.addStretch()
            voice_message = CVoiceMessageWidget(audio_data=voice, alignment=Qt.AlignRight, has_dot=True)
            container_layout.addWidget(voice_message)
            avatar_right = CAvatar(shape=CAvatar.Circle, url=icons['avatar_m.jpeg'], size=CAvatar.SizeSmall)
            container_layout.addWidget(avatar_right)
        else:
            avatar_left = CAvatar(shape=CAvatar.Rectangle, url=icons['avatar_w.jpeg'], size=CAvatar.SizeSmall)
            container_layout.addWidget(avatar_left)
            voice_message = CVoiceMessageWidget(audio_data=voice, alignment=Qt.AlignLeft, has_dot=True)
            container_layout.addWidget(voice_message)
            container_layout.addStretch()
        container_layout.setContentsMargins(10, 5, 10, 5)
        self.chat_display_layout.addWidget(message_container)
        # 滚动到底部
        self.chat_display_area.verticalScrollBar().setValue(self.chat_display_area.verticalScrollBar().maximum())
        # 有时候滚动行为在画面刷新之前，导致没有滚动到底部，这里补一个延迟滚动。
        QTimer.singleShot(100, lambda: self.chat_display_area.verticalScrollBar().setValue(
            self.chat_display_area.verticalScrollBar().maximum()))


if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = SpeechInterface()
    MTheme(theme='dark').apply(demo_widget)
    # 显示窗口
    demo_widget.show()
    loop.run_forever()
