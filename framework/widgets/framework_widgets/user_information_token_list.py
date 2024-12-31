import os

import qasync
import asyncio

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout

from db.pickle_db.data_storage_service import data_local_storage_authorization
from framework.api.auth import api_logout_user_by_satoken, api_login_list
from framework.widgets.cocos_widgets import CMessageDialog
from framework.widgets.cocos_widgets.c_card_list import CCardList
from framework.widgets.dayu_widgets import MLabel, MLineEdit, MToolButton, MPushButton
from resources.framework.icons import icons


class TokenWidget(QWidget):
    def __init__(self, parent, device: str, token: str):
        super(TokenWidget, self).__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.parent = parent
        self.device = device
        self.token = token

        qh_box_layout = QHBoxLayout()
        qh_box_layout.addWidget(MLabel(device))
        qh_box_layout.setAlignment(Qt.AlignCenter)
        self.layout.addLayout(qh_box_layout)

        line_edit = MLineEdit(self)
        m_tool_button = MToolButton().svg(icons['token.svg']).icon_only()

        def tool_button_handle():
            line_edit.selectAll()
            clipboard = QApplication.clipboard()
            clipboard.setText(line_edit.selectedText())
            CMessageDialog.success("Copied", parent=self)

        m_tool_button.clicked.connect(tool_button_handle)
        line_edit.set_prefix_widget(m_tool_button)
        line_edit.setText(token)
        self.layout.addWidget(line_edit)

        q_button_clear = MPushButton("清退")
        q_button_clear.clicked.connect(self.logout)
        self.layout.addWidget(q_button_clear)

    def logout(self):
        token = data_local_storage_authorization.get("token")
        api_logout_user_by_satoken(satoken=token, logout_token=self.token)
        self.parent.load_token_list()
        if token == self.token:
            # 清除用户数据
            data_local_storage_authorization.set("nickname", None)
            data_local_storage_authorization.set("total_token", None)
            data_local_storage_authorization.set("online_token", None)
            data_local_storage_authorization.set("mobile", None)
            data_local_storage_authorization.set("expirationDate", None)


class UserInformationTokenListWidget(QWidget):
    def __init__(self, parent=None):
        super(UserInformationTokenListWidget, self).__init__(parent)
        self.parent = parent
        self.setWindowTitle("令牌列表")
        # setup_main_theme(self)
        # 布局
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        # 创建窗口
        self.token_list_widget = CCardList()
        self.main_layout.addWidget(self.token_list_widget)
        self.personal_button = MPushButton("个人中心")
        self.load_token_list()

    def load_token_list(self):
        # 清空布局中的所有控件
        # 清空布局中的所有控件
        while self.token_list_widget.task_card_lay.count():
            item = self.token_list_widget.task_card_lay.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        token = data_local_storage_authorization.get("token")
        if token:
            token_list = api_login_list(token)
            if token_list:
                for key, value in token_list.items():
                    if token == key:
                        # 本机
                        value = f'<span style="color: red; font-size: 16px;"><b>{value}</b></span>'
                    self.token_list_widget.add_setting(
                        widget=TokenWidget(self, value, key))

        self.token_list_widget.task_card_lay.addStretch()
        self.token_list_widget.add_setting(widget=self.personal_button)


if __name__ == "__main__":
    # 创建主循环
    app = QApplication()
    # 创建异步事件循环
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    main_window = UserInformationTokenListWidget()
    token_list = [
        {'device': '电脑端', 'token': 'b3ff8b86-8f04-40ac-8be9-4f152329c68e'},
        {'device': '手机端', 'token': 'b3ff8b86-8f04-40ac-8be9-4f152329c68e'},
        {'device': 'device3', 'token': 'b3ff8b86-8f04-40ac-8be9-4f152329c68e'},
        {'device': 'device4', 'token': 'b3ff8b86-8f04-40ac-8be9-4f152329c68e'},
        {'device': 'device4', 'token': 'b3ff8b86-8f04-40ac-8be9-4f152329c68e'},
        {'device': 'device4', 'token': 'b3ff8b86-8f04-40ac-8be9-4f152329c68e'},
        {'device': 'device4', 'token': 'b3ff8b86-8f04-40ac-8be9-4f152329c68e'},
        {'device': 'device4', 'token': 'b3ff8b86-8f04-40ac-8be9-4f152329c68e'},
    ]
    main_window.show()
    with loop:
        loop.run_forever()
