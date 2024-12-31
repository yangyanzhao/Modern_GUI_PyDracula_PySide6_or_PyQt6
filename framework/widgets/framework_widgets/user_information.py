import os

import qasync

from framework.utils.position_util import center_point_alignment
from framework.widgets.cocos_widgets import CAvatar
from framework.widgets.dayu_widgets import MLabel, MFieldMixin, MPushButton
from resources.framework.icons import icons

import asyncio

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout

from db.pickle_db.data_storage_service import data_local_storage_authorization


class InforWidget(QWidget):
    def __init__(self, avatar: CAvatar = None, name: str = None, value: str = None):
        super(InforWidget, self).__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.avatar = avatar
        self.name = name
        self.value = value

        if avatar:
            qh_box_layout = QHBoxLayout()
            qh_box_layout.addWidget(avatar)
            qh_box_layout.setAlignment(Qt.AlignCenter)
            self.layout.addLayout(qh_box_layout)

        if name:
            self.q_label_name = MLabel(name)
            self.q_label_name.setWordWrap(True)
            self.q_label_name.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(self.q_label_name)

        if value:
            self.q_label_value = MLabel(value)
            self.q_label_value.setWordWrap(True)
            self.q_label_value.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(self.q_label_value)


class UserInformationWidget(QWidget, MFieldMixin):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("个人中心")
        # setup_main_theme(self)

        # 主布局-垂直
        self.main_layout = QVBoxLayout(self)
        # 头像
        self.avatar_layout = QHBoxLayout(self)
        c_avatar = CAvatar(shape=CAvatar.Rectangle, size=QSize(200, 150),
                           url=icons['avatar.jpg'], is_OD=True,
                           animation=False, parent=self)
        self.avatar_layout.addWidget(c_avatar)

        # 昵称 总数 在线
        self.post_layout = QHBoxLayout(self)
        infor_widget_0 = InforWidget(
            name=f"<span style='color: #7bb8d7;font-family: KaiTi;font-size: 14px; font-weight: bold;'>昵称</span>",
            value="HCP实施部")
        data_local_storage_authorization.widget_bind_value(
            widget=infor_widget_0.q_label_value,
            local_field_name="nickname",
            widget_property="text")
        self.post_layout.addWidget(infor_widget_0)

        infor_widget_1 = InforWidget(
            name=f"<span style='color: #7bb8d7;font-family: KaiTi;font-size: 14px; font-weight: bold;'>总数</span>",
            value="10")
        data_local_storage_authorization.widget_bind_value(
            widget=infor_widget_1.q_label_value,
            local_field_name="total_token",
            widget_property="text")
        self.post_layout.addWidget(infor_widget_1)

        infor_widget_2 = InforWidget(
            name=f"<span style='color: #7bb8d7;font-family: KaiTi;font-size: 14px; font-weight: bold;'>在线</span>",
            value="1")
        data_local_storage_authorization.widget_bind_value(
            local_field_name="online_token",
            widget=infor_widget_2.q_label_value,
            widget_property="text")
        self.post_layout.addWidget(infor_widget_2)

        self.post_layout.setStretch(0, 1)
        self.post_layout.setStretch(1, 1)
        self.post_layout.setStretch(2, 1)
        # 手机 地址
        self.phone_address_layout = QHBoxLayout(self)
        c_avatar_phone = CAvatar(shape=CAvatar.Circle, size=CAvatar.SizeSmall,
                                 url=icons['手机.svg'])
        infor_widget_3 = InforWidget(avatar=c_avatar_phone,
                                     name=f"<span style='color: #808080;font-family: KaiTi;font-size: 14px;'>手机</span>",
                                     value="13888888888")
        data_local_storage_authorization.widget_bind_value(local_field_name="mobile",
                                                           widget=infor_widget_3.q_label_value,
                                                           widget_property="text")
        self.phone_address_layout.addWidget(infor_widget_3)

        c_avatar_address = CAvatar(shape=CAvatar.Circle, size=CAvatar.SizeSmall,
                                   url=icons['过期时间.svg'], animation=True)
        infor_widget_4 = InforWidget(avatar=c_avatar_address,
                                     name=f"<span style='color: #808080;font-family: KaiTi;font-size: 14px;'>过期时间</span>",
                                     value="2024:11:16 21:12:00")
        data_local_storage_authorization.widget_bind_value(
            local_field_name="expirationDate",
            widget=infor_widget_4.q_label_value,
            widget_property="text")
        self.phone_address_layout.addWidget(infor_widget_4)
        self.phone_address_layout.setStretch(0, 2)
        self.phone_address_layout.setStretch(1, 3)

        self.rout_layout = QVBoxLayout(self)
        self.button_logout = MPushButton(text="登录")
        self.button_logout.clicked.connect(self.logout)
        self.rout_layout.addWidget(self.button_logout)

        self.login_list_layout = QVBoxLayout(self)
        self.button_login_list = MPushButton(text="在线列表")
        self.login_list_layout.addWidget(self.button_login_list)

        # 设置主布局
        self.setLayout(self.main_layout)
        self.main_layout.addLayout(self.avatar_layout)
        self.main_layout.addLayout(self.post_layout)
        self.main_layout.addLayout(self.phone_address_layout)
        self.main_layout.addLayout(self.rout_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.login_list_layout)

    def load_data(self):
        # 访问API获取最新用户信息

        pass

    def logout(self):
        if self.parent:
            center_point_alignment(self.parent, self.parent.login_dialog_wrapper)
            check = self.parent.login_dialog_wrapper.target_widget.check_token()
            if check:
                self.parent.login_dialog_wrapper.show()


if __name__ == "__main__":
    # 创建主循环
    app = QApplication()
    # 创建异步事件循环
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    main_window = UserInformationWidget()
    main_window.show()
    with loop:
        loop.run_forever()
