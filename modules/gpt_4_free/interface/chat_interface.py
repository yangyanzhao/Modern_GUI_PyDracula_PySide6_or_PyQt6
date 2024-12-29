import asyncio
import logging
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
from PySide6.QtCore import Qt, Signal, QTimer

from qasync import QEventLoop

from db.mysql.async_utils import is_in_async_context
from framework.widgets.cocos_widgets.c_avatar import CAvatar
from framework.widgets.cocos_widgets.c_splash_screen.c_splash_screen import increase_counter
from framework.widgets.dayu_widgets import MTheme
from framework.widgets.dayu_widgets.combo_box import MComboBox
from framework.widgets.dayu_widgets.field_mixin import MFieldMixin
from framework.widgets.dayu_widgets.label import MLabel
from framework.widgets.dayu_widgets.menu import MMenu
from framework.widgets.dayu_widgets.push_button import MPushButton
from framework.widgets.dayu_widgets.text_edit import MTextEdit
from modules.gpt_4_free.api.baixiaoying.baixiaoying_api_one import BaichuanAPIOne
from modules.gpt_4_free.api.baixiaoying.baixiaoying_api_three import BaichuanAPIThree
from modules.gpt_4_free.api.baixiaoying.baixiaoying_api_two import BaichuanAPITwo
from modules.gpt_4_free.api.dedao.dedao_api_one import DeDaoAPIOne
from modules.gpt_4_free.api.deepseek.deepseek_free_api_four import DeepseekAPIFour
from modules.gpt_4_free.api.deepseek.deepseek_free_api_one import DeepseekAPIOne
from modules.gpt_4_free.api.deepseek.deepseek_free_api_three import DeepseekAPIThree
from modules.gpt_4_free.api.deepseek.deepseek_free_api_two import DeepseekAPITwo
from modules.gpt_4_free.api.doubao.doubao_free_api_one import DouBaoAPIOne
from modules.gpt_4_free.api.doubao.doubao_free_api_two import DouBaoAPITwo
from modules.gpt_4_free.api.doubao.jimeng_free_api_one import JiMengAPIOne
from modules.gpt_4_free.api.doubao.jimeng_free_api_two import JiMengAPITwo
from modules.gpt_4_free.api.glm.glm_free_api_four import GlmAPIFour
from modules.gpt_4_free.api.glm.glm_free_api_one import GlmAPIOne
from modules.gpt_4_free.api.glm.glm_free_api_three import GlmAPIThree
from modules.gpt_4_free.api.glm.glm_free_api_two import GlmAPITwo
from modules.gpt_4_free.api.hailuo.hailuo_free_api_four import HailuoAPIFour
from modules.gpt_4_free.api.hailuo.hailuo_free_api_one import HailuoAPIOne
from modules.gpt_4_free.api.hailuo.hailuo_free_api_three import HailuoAPIThree
from modules.gpt_4_free.api.hailuo.hailuo_free_api_two import HailuoAPITwo
from modules.gpt_4_free.api.hunyuan.hunyuan_api_one import HunYuanAPIOne
from modules.gpt_4_free.api.luca.luca_api_one import LucaAPIOne
from modules.gpt_4_free.api.metaso.metaso_free_api_four import MetasoAPIFour
from modules.gpt_4_free.api.metaso.metaso_free_api_one import MetasoAPIOne
from modules.gpt_4_free.api.metaso.metaso_free_api_three import MetasoAPIThree
from modules.gpt_4_free.api.metaso.metaso_free_api_two import MetasoAPITwo
from modules.gpt_4_free.api.qwen.qwen_free_api_four import QwenAPIFour
from modules.gpt_4_free.api.qwen.qwen_free_api_one import QwenAPIOne
from modules.gpt_4_free.api.qwen.qwen_free_api_three import QwenAPIThree
from modules.gpt_4_free.api.qwen.qwen_free_api_two import QwenAPITwo
from modules.gpt_4_free.api.sensetime.sensetime_api import SensetimeAPIOne
from modules.gpt_4_free.api.shanhai.shanhai_api_one import ShanHaiAPIOne
from modules.gpt_4_free.api.shusheng.shusheng_api_one import ShushengAPIOne
from modules.gpt_4_free.api.shusheng.shusheng_api_three import ShushengAPIThree
from modules.gpt_4_free.api.shusheng.shusheng_api_two import ShushengAPITwo
from modules.gpt_4_free.api.spark.spark_free_api_one import SparkAPIOne
from modules.gpt_4_free.api.spark.spark_free_api_two import SparkAPITwo
from modules.gpt_4_free.api.step.step_free_api_four import StepAPIFour
from modules.gpt_4_free.api.step.step_free_api_one import StepAPIOne
from modules.gpt_4_free.api.step.step_free_api_three import StepAPIThree
from modules.gpt_4_free.api.step.step_free_api_two import StepAPITwo
from modules.gpt_4_free.api.tigerbot.tigerbot_api_one import TigerbotAPIOne
from modules.gpt_4_free.api.yayi.yayi_api_one import YayiAPIOne
from modules.gpt_4_free.api.yayi.yayi_api_two import YayiAPITwo
from modules.gpt_4_free.api.yi.yi_api_one import YiApiOne
from modules.gpt_4_free.api.yiyan.yiyan_api_one import YiyanAPIOne
from modules.gpt_4_free.api.zhinao360.zhinao360_api_one import Zhinao360ApiOne
from modules.gpt_4_free.api.zhinao360.zhinao360_api_two import Zhinao360ApiTwo
from modules.gpt_4_free.icons import icons

# 大模型映射
llm_mapping = {
    "deepseek-one": DeepseekAPIOne,
    "deepseek-two": DeepseekAPITwo,
    "deepseek-three": DeepseekAPIThree,
    "deepseek-four": DeepseekAPIFour,
    "glm-one": GlmAPIOne,
    "glm-two": GlmAPITwo,
    "glm-three": GlmAPIThree,
    "glm-four": GlmAPIFour,
    "doubao-one": DouBaoAPIOne,
    "doubao-two": DouBaoAPITwo,
    "jimeng-one": JiMengAPIOne,
    "jimeng-two": JiMengAPITwo,
    "qwen-one": QwenAPIOne,
    "qwen-two": QwenAPITwo,
    "qwen-three": QwenAPIThree,
    "qwen-four": QwenAPIFour,
    "step-one": StepAPIOne,
    "step-two": StepAPITwo,
    "step-three": StepAPIThree,
    "step-four": StepAPIFour,
    "hailuo-one": HailuoAPIOne,
    "hailuo-two": HailuoAPITwo,
    "hailuo-three": HailuoAPIThree,
    "hailuo-four": HailuoAPIFour,
    "metaso-one": MetasoAPIOne,
    "metaso-two": MetasoAPITwo,
    "metaso-three": MetasoAPIThree,
    "metaso-four": MetasoAPIFour,
    "spark-one": SparkAPIOne,
    "spark-two": SparkAPITwo,
    "baichuan-one": BaichuanAPIOne,
    "baichuan-two": BaichuanAPITwo,
    "baichuan-three": BaichuanAPIThree,
    "shanhai-one": ShanHaiAPIOne,
    "tigerbot-one": TigerbotAPIOne,
    "yayi-one": YayiAPIOne,
    "yayi-two": YayiAPITwo,
    "yi-one": YiApiOne,
    "yiyan-one": YiyanAPIOne,
    "zhinao360-one": Zhinao360ApiOne,
    "zhinao360-two": Zhinao360ApiTwo,
    "sensetime-one": SensetimeAPIOne,
    "shusheng-one": ShushengAPIOne,
    "shusheng-two": ShushengAPITwo,
    "shusheng-three": ShushengAPIThree,
    "luca-one": LucaAPIOne,
    "dedao-one": DeDaoAPIOne,
    "hunyuan-one": HunYuanAPIOne,
}
# 大模型菜单
llm_menu_list = [
    {
        "label": "智谱清言",
        "children": [
            {
                "label": "glm-one",
                "value": "glm-one"
            },
            {
                "label": "glm-two",
                "value": "glm-two"
            },
            {
                "label": "glm-three",
                "value": "glm-three"
            },
            {
                "label": "glm-four",
                "value": "glm-four"
            }
        ]
    },
    {
        "label": "深度求索",
        "children": [
            {
                "label": "deepseek-one",
                "value": "deepseek-one"
            },
            {
                "label": "deepseek-two",
                "value": "deepseek-two"
            },
            {
                "label": "deepseek-three",
                "value": "deepseek-three"
            },
            {
                "label": "deepseek-four",
                "value": "deepseek-four"
            }
        ]
    },
    {
        "label": "豆包",
        "children": [
            {
                "label": "doubao-one",
                "value": "doubao-one"
            },
            {
                "label": "doubao-two",
                "value": "doubao-two"
            },
            {
                "label": "jimeng-one",
                "value": "jimeng-one"
            },
            {
                "label": "jimeng-two",
                "value": "jimeng-two"
            },
        ]
    },
    {
        "label": "通义千问",
        "children": [
            {
                "label": "qwen-one",
                "value": "qwen-one"
            },
            {
                "label": "qwen-two",
                "value": "qwen-two"
            },
            {
                "label": "qwen-three",
                "value": "qwen-three"
            },
            {
                "label": "qwen-four",
                "value": "qwen-four"
            },
        ]
    },
    {
        "label": "跃阶",
        "children": [
            {
                "label": "step-one",
                "value": "step-one"
            },
            {
                "label": "step-two",
                "value": "step-two"
            },
            {
                "label": "step-three",
                "value": "step-three"
            },
            {
                "label": "step-four",
                "value": "step-four"
            },
        ]
    },
    {
        "label": "海螺",
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
    {
        "label": "秘塔",
        "children": [
            {
                "label": "metaso-one",
                "value": "metaso-one"
            },
            {
                "label": "metaso-two",
                "value": "metaso-two"
            },
            {
                "label": "metaso-three",
                "value": "metaso-three"
            },
            {
                "label": "metaso-four",
                "value": "metaso-four"
            },
        ]
    },
    {
        "label": "讯飞星火",
        "children": [
            {
                "label": "spark-one(已被封号)",
                "value": "spark-one"
            },
            {
                "label": "spark-two",
                "value": "spark-two"
            },
        ]
    },
    {
        "label": "百小应",
        "children": [
            {
                "label": "baichuan-one",
                "value": "baichuan-one"
            },
            {
                "label": "baichuan-two",
                "value": "baichuan-two"
            },
            {
                "label": "baichuan-three",
                "value": "baichuan-three"
            },
        ]
    },
    {
        "label": "山海",
        "children": [
            {
                "label": "shanhai-one",
                "value": "shanhai-one"
            }
        ]
    },
    {
        "label": "虎博",
        "children": [
            {
                "label": "tigerbot-one",
                "value": "tigerbot-one"
            }
        ]
    },
    {
        "label": "雅意",
        "children": [
            {
                "label": "yayi-one",
                "value": "yayi-one"
            },
            {
                "label": "yayi-two",
                "value": "yayi-two"
            }
        ]
    },
    {
        "label": "一",
        "children": [
            {
                "label": "yi-one",
                "value": "yi-one"
            }
        ]
    },
    {
        "label": "文心一言",
        "children": [
            {
                "label": "yiyan-one",
                "value": "yiyan-one"
            }
        ]
    },
    {
        "label": "智脑360",
        "children": [
            {
                "label": "zhinao360-one",
                "value": "zhinao360-one"
            },
            {
                "label": "zhinao360-two",
                "value": "zhinao360-two"
            }
        ]
    },
    {
        "label": "商量",
        "children": [
            {
                "label": "sensetime-one",
                "value": "sensetime-one"
            }
        ]
    },
    {
        "label": "书生",
        "children": [
            {
                "label": "shusheng-one",
                "value": "shusheng-one"
            },
            {
                "label": "shusheng-two",
                "value": "shusheng-two"
            }, {
                "label": "shusheng-three",
                "value": "shusheng-three"
            }
        ]
    },
    {
        "label": "面壁",
        "children": [
            {
                "label": "luca-one",
                "value": "luca-one"
            }
        ]
    },
    {
        "label": "得到",
        "children": [
            {
                "label": "dedao-one",
                "value": "dedao-one"
            }
        ]
    },
    {
        "label": "混元",
        "children": [
            {
                "label": "hunyuan-one",
                "value": "hunyuan-one"
            }
        ]
    },
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


class ChatInterface(QWidget, MFieldMixin):
    def __init__(self, parent=None):
        increase_counter("GPT聊天初始化...")
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
        self.llm_box.setMaximumWidth(150)
        self.llm_box.setMinimumWidth(100)
        menu = MMenu(cascader=True, parent=self)
        menu.set_data(llm_menu_list)
        self.llm_box.set_menu(menu)
        self.input_text = CustomTextEdit()
        self.input_text.returnPressed.connect(self.send_message)

        self.send_button = MPushButton("发送")
        self.send_button.clicked.connect(self.send_message)

        self.input_layout.addWidget(self.llm_box)
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
            label_ing = MLabel("正在思考中...")
            self.display_label(label_ing, alignment=Qt.AlignLeft)
            self.input_text.clear()
            self.visitor_llm(message, label_ing)

    def visitor_llm(self, message, label_ing: QLabel):
        # 访问LLM API
        llm_select = self.llm_box.currentText()
        # 判断是否处于某个loop中
        if is_in_async_context():
            loop = asyncio.get_running_loop()
            # 当前loop是否正在运行
            if loop.is_running():
                result_future = asyncio.run_coroutine_threadsafe(llm_mapping[llm_select].main_chat(message), loop)
                try:
                    # 设置超时时间
                    result = result_future.result(timeout=180)
                    label_ing.setText(result)
                except asyncio.TimeoutError:
                    logging.error("Task timed out after 180 seconds")
                    label_ing.setText("Task timed out after 180 seconds")
                except Exception as e:
                    logging.error(f"Task failed: {e}\n{traceback.format_exc()}")
                    label_ing.setText(f"Task failed: {e}\n{traceback.format_exc()}")
            else:
                result = loop.run_until_complete(llm_mapping[llm_select].main_chat(message))
                label_ing.setText(result)
        else:
            result = asyncio.run(llm_mapping[llm_select].main_chat(message))
            label_ing.setText(result)

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


if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = ChatInterface()
    # 显示窗口
    demo_widget.show()
    loop.run_forever()