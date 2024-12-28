import asyncio
import logging
import random

from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout
from qasync import QEventLoop

from db.pickle_db.pickle_jdbc import pickle
from framework.widgets.dayu_widgets import MTheme
from framework.widgets.dayu_widgets.field_mixin import MFieldMixin
from framework.widgets.dayu_widgets.label import MLabel
from framework.widgets.dayu_widgets.line_edit import MLineEdit
from framework.widgets.dayu_widgets.push_button import MPushButton

"""
作为pickle键值数据库的一个应用

SessionStorage和LocalStorage
"""


# 作为数据SessionStorage存储类
class DataSessionStorage(MFieldMixin):
    def __init__(self, scope):
        """
        :param scope: 作用域。防止key冲突，对于不同的业务采用不同的域。
        """
        self.scope = scope  # 作用域
        super(DataSessionStorage, self).__init__()

    def widget_bind_value(self, widget: QWidget, session_field_name: str, widget_property: str,
                          widget_signal: str = None, callback=None):
        """
        控件数据绑定数据，双向绑定
        :param widget: 绑定控件
        :param session_field_name: 字段名称（用户自定义，取名儿不要冲突）
        :param widget_property: 控件属性名称（不知道属性的，可以用后边的方法进行遍历）
        :param widget_signal: 控件的数据改变信号（不知道信号的，可以用后边的方法进行遍历），如果不传，则时单项绑定，数据绑定到控件，但是控件自身数据改变不会通过信号回传到本地数据中。
        :param callback: 数据发生改变时的主动回调，一般不传入。
        """
        session_field = f"{self.scope}.{session_field_name}"
        # 检测是否已经注册过该字段
        if self.props_dict is None or session_field not in self.props_dict:
            # 注册属性
            self.register_field(name=session_field)
        self.bind(data_name=session_field, widget=widget,
                  qt_property=widget_property,
                  signal=widget_signal, callback=callback)

    def widget_bind_computed_value(self, widget: QWidget, session_field_name: str, getter, widget_property: str,
                                   widget_signal: str = None, callback=None):
        """
        绑定计算属性，将控件的值绑定到计算属性上。
        :param widget: 绑定控件
        :param session_field_name: 字段名称（用户自定义，取名儿不要冲突）
        :param getter: 获取值的计算函数
        :param widget_property: 控件属性名称（不知道属性的，可以用后边的方法进行遍历）
        :param widget_signal: 控件的数据改变信号（不知道信号的，可以用后边的方法进行遍历），如果不传，则时单项绑定，数据绑定到控件，但是控件自身数据改变不会通过信号回传到本地数据中。
        :param callback: 数据发生改变时的主动回调，一般不传入。
        """
        session_field = f"{self.scope}.computed.{session_field_name}"
        # 检测是否已经注册过该字段
        if self.computed_dict is None or session_field not in self.computed_dict:
            # 注册属性
            self.register_field(name=session_field, getter=getter)
        self.bind(data_name=session_field, widget=widget,
                  qt_property=widget_property,
                  signal=widget_signal, callback=callback)

    def get(self, session_field_name, none_or_else=None):
        """
        获取session中的数据
        """
        session_field = f"{self.scope}.{session_field_name}"
        if self.props_dict is None:
            self.props_dict = {}
        if self.computed_dict is None:
            self.computed_dict = {}
        if session_field in self.props_dict or session_field in self.computed_dict:
            if self.field(session_field):
                return self.field(session_field)
        return none_or_else

    def set(self, session_field_name, value):
        """
        设置session中的数据
        """
        session_field = f"{self.scope}.{session_field_name}"
        if self.props_dict is None or session_field not in self.props_dict:
            self.register_field(name=session_field)
        self.set_field(session_field, value)


# 作为数据LocalStorage存储类,与pickle键值数据库配合使用
class DataLocalStorage(MFieldMixin):
    def __init__(self, scope):
        """
        :param scope: 作用域。防止key冲突，对于不同的业务采用不同的域。
        """
        self.scope = scope  # 作用域
        # self.table_local_storage = TINY_DB_LOCAL_STORAGE.table(f"LocalStorage.{self.scope}")  # LocalStorage本地存储
        super(DataLocalStorage, self).__init__()
        self.init_set()  # 初始化pickle_jdbc数据到memory中。

    def widget_bind_value(self, widget: QWidget, local_field_name: str, widget_property: str,
                          widget_signal: str = None, callback=None):
        """
        控件数据绑定数据，用来记住数据回显，使控件有记忆力。
        :param widget: 绑定控件
        :param local_field_name: 字段名称（用户自定义，取名儿不要冲突）
        :param widget_property: 控件属性名称（不知道属性的，可以用后边的方法进行遍历）
        :param widget_signal: 控件的数据改变信号（不知道信号的，可以用后边的方法进行遍历）
        :param callback: 数据发生改变时的主动回调，一般不传入。
        :return:
        """
        local_field = f"{self.scope}.{local_field_name}"
        # 检测是否已经注册过该字段
        if self.props_dict is None or local_field not in self.props_dict:
            # 注册属性
            self.register_field(name=local_field)
        # 尝试从pickle中获取配置
        field_data = pickle.get(local_field)
        if field_data:
            # 设置成读取值
            self.set_field(name=local_field, value=field_data)
        else:
            # 设置成控件属性值
            self.set_field(name=local_field, value=widget.property(widget_property))
        # 绑定
        if callback:
            # 在数据改变时，通过回调更到新数据库
            self.bind(data_name=local_field, widget=widget, qt_property=widget_property,
                      signal=widget_signal,
                      callback=lambda: (pickle.set(local_field, self.field(local_field)), callback()))
        else:
            self.bind(data_name=local_field, widget=widget, qt_property=widget_property,
                      signal=widget_signal,
                      callback=lambda: pickle.set(local_field, self.field(local_field)))

    def widget_bind_computed_value(self, widget: QWidget, local_field_name: str, getter, widget_property: str,
                                   widget_signal: str = None, callback=None):
        """
        绑定计算属性，将控件的值绑定到计算属性上。
        :param widget: 绑定控件
        :param local_field_name: 字段名称（用户自定义，取名儿不要冲突）
        :param getter: 获取值的计算函数
        :param widget_property: 控件属性名称（不知道属性的，可以用后边的方法进行遍历）
        :param widget_signal: 控件的数据改变信号（不知道信号的，可以用后边的方法进行遍历），如果不传，则时单项绑定，数据绑定到控件，但是控件自身数据改变不会通过信号回传到本地数据中。
        :param callback: 数据发生改变时的主动回调，一般不传入。
        """
        local_field = f"{self.scope}.computed.{local_field_name}"
        # 检测是否已经注册过该字段
        if self.computed_dict is None or local_field not in self.computed_dict:
            # 注册属性
            self.register_field(name=local_field, getter=getter)
        self.bind(data_name=local_field, widget=widget,
                  qt_property=widget_property,
                  signal=widget_signal, callback=callback)

    def get(self, local_field_name: str, none_or_else=None):
        """
        获取数据
        """
        local_field = f"{self.scope}.{local_field_name}"
        value_memory = None
        # 有两种方式，一种是直接从数据库中获取，一种是从本地属性中获取。
        # 从数据库中获取数据
        value_pickle = pickle.get(local_field)

        # 从本地属性中获取数据
        if self.props_dict is None:
            self.props_dict = {}
        if self.computed_dict is None:
            self.computed_dict = {}
        if local_field in self.props_dict or local_field in self.computed_dict:
            value_memory = self.field(local_field)

        # 这里做一个数据一致性检查，如果数据不一致，则抛出异常。
        if value_pickle and value_pickle != value_memory:
            raise ValueError("数据不一致，请检查数据是否一致。")
        if value_pickle:
            return value_pickle
        else:
            return none_or_else

    def set(self, local_field_name: str, value):
        """
        设置数据
        这里有两种行为
        1、设置控件绑定过的数据，用来控制控件行为。这种情况，只需要设置内存的值就可以，pickle的值会通过回调设置进去。
        2、用于存储数据，比如token等信息，仅仅是用来存储和获取的，与控件无关。这种情况下有两个问题，
            2.1、 仅仅设置内存值是不够的，因为没有绑定相关控件，无法通过回调设置进pickle,所以要设置两次。
            2.2、 在初始化的时候，没有控件进行触发set的过程。也就是说初始化的时候，无法将pickle中的数据设置到memory中。
        综上所述，为了保证成功，设置的时候，统一设置两次。且在初始化的时候要将pickle中的数据内置到memory中，也就是要在初始化的时候手动调用set()方法。
        """
        local_field = f"{self.scope}.{local_field_name}"
        if self.props_dict is None or local_field not in self.props_dict:
            self.register_field(name=local_field)
        self.set_field(local_field, value)
        pickle.set(local_field, self.field(local_field))

    def init_set(self):
        if self.scope in pickle_data and pickle_data[self.scope] and isinstance(pickle_data[self.scope], dict):
            for key, value in pickle_data[self.scope].items():
                if self.props_dict is None or key not in self.props_dict:
                    self.register_field(name=key)
                self.set_field(key, pickle.get(key))


# 获取pickle 中的所有键
pickle_keys = pickle.getall()
# 对键值对的命名空间进行分组
# 用于存储分组后的字典
pickle_data = {}

# 遍历原始字典
for key in pickle_keys:
    # 分割key，获取namespace和business key
    # 如果key中没有.或者有多个·，则跳过
    if '.' not in key or key.count('.') > 1:
        continue
    namespace, business_key = key.split('.', 1)
    # 如果namespace不存在于grouped_data中，则创建一个新的字典
    if namespace not in pickle_data:
        pickle_data[namespace] = {}
    # 将键值对添加到对应的namespace字典中
    pickle_data[namespace][key] = pickle.get(key)

# 框架默认存储器
data_session_storage_py_one_dark = DataSessionStorage(scope="py_one_dark")
data_local_storage_py_one_dark = DataLocalStorage(scope="py_one_dark")

# 框架默认存储器
data_session_storage_authorization = DataSessionStorage(scope="authorization")
data_local_storage_authorization = DataLocalStorage(scope="authorization")

# 微信存储器
data_session_storage_wechat = DataSessionStorage(scope="wechat")
data_local_storage_wechat = DataLocalStorage(scope="wechat")

# 知乎存储器
data_session_storage_zhihu = DataSessionStorage(scope="zhihu")
data_local_storage_zhihu = DataLocalStorage(scope="zhihu")

# SpringCloud存储器
data_session_storage_spring_cloud = DataSessionStorage(scope="spring_cloud")
data_local_storage_spring_cloud = DataLocalStorage(scope="spring_cloud")


class DemoSessionWidget(QWidget):
    def __init__(self):
        super(DemoSessionWidget, self).__init__()
        layout = QVBoxLayout(self)
        line_edit = MLineEdit()
        line_edit.setPlaceholderText("请输入你的名字：")
        layout.addWidget(line_edit)
        # 双向绑定到session 中。
        data_session_storage_py_one_dark.widget_bind_value(widget=line_edit, session_field_name="name",
                                                           widget_property="text",
                                                           widget_signal="textChanged", callback=None)

        label1 = MLabel()
        # 将显示内容绑定到name 字段上
        data_session_storage_py_one_dark.widget_bind_value(widget=label1, session_field_name="name",
                                                           widget_property="text")
        layout.addWidget(label1)

        button1 = MPushButton("获取name数据")
        button1.clicked.connect(lambda: print(data_session_storage_py_one_dark.get("name")))
        layout.addWidget(button1)

        button2 = MPushButton("随机name数据")
        button2.clicked.connect(lambda: data_session_storage_py_one_dark.set("name", random.randint(0, 100)))
        layout.addWidget(button2)

        button3 = MPushButton("设置AGE数据")
        button3.clicked.connect(lambda: data_session_storage_py_one_dark.set("age", random.randint(-100, 0)))
        layout.addWidget(button3)

        button4 = MPushButton("获取AGE数据")
        button4.clicked.connect(lambda: print(data_session_storage_py_one_dark.get("age")))
        layout.addWidget(button4)


class DemoLocalWidget(QWidget):
    def __init__(self):
        super(DemoLocalWidget, self).__init__()
        layout = QVBoxLayout(self)
        line_edit = MLineEdit()
        line_edit.setPlaceholderText("请输入你的名字：")
        layout.addWidget(line_edit)
        # 双向绑定到session 中。
        data_local_storage_py_one_dark.widget_bind_value(widget=line_edit, local_field_name="name",
                                                         widget_property="text",
                                                         widget_signal="textChanged", callback=None)

        label1 = MLabel()
        # 将显示内容绑定到name 字段上
        data_local_storage_py_one_dark.widget_bind_value(widget=label1, local_field_name="name", widget_property="text")
        layout.addWidget(label1)

        button1 = MPushButton("获取name数据")
        button1.clicked.connect(lambda: print(data_local_storage_py_one_dark.get("name")))
        layout.addWidget(button1)

        button2 = MPushButton("随机name数据")
        button2.clicked.connect(lambda: data_local_storage_py_one_dark.set("name", random.randint(0, 100)))
        layout.addWidget(button2)

        button3 = MPushButton("设置AGE数据")
        button3.clicked.connect(lambda: data_local_storage_py_one_dark.set("age", random.randint(-100, 0)))
        layout.addWidget(button3)

        button4 = MPushButton("获取AGE数据")
        button4.clicked.connect(lambda: print(data_local_storage_py_one_dark.get("age")))
        layout.addWidget(button4)



if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = DemoLocalWidget()
    MTheme(theme='dark').apply(demo_widget)
    # 显示窗口
    demo_widget.show()
    loop.run_forever()
