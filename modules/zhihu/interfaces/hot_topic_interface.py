import asyncio
import datetime
import logging

from PySide2.QtWidgets import QApplication
from dayu_widgets.qt import MIcon
from qasync import QEventLoop
from dayu_widgets import MTheme, MPushButton

from gui.uis.windows.startup_window.main import increase_counter
from gui.utils.dialog_util import are_you_sure_dialog
from gui.widgets.c_table_view_widget.table_view_mysql_widget import TableViewWidgetMySQLAbstract
from gui.widgets.c_table_view_widget.table_view_widget import ColumnConfig
from modules.zhihu_auto.api.resource.douyin_hot_topic_spider import DouyinHotTopicSpider
from modules.zhihu_auto.api.resource.picture_pixabay_spider import PicturePixabaySpider
from modules.zhihu_auto.api.resource.weibo_hot_topic_spider import WeiboHotTopicSpider
from modules.zhihu_auto.icons import icons

"""
热点管理
"""


class HotTopicsInterface(TableViewWidgetMySQLAbstract):
    DATABASE_NAME = "zhihu"
    TABLE_NAME = "hot_topics"

    def __init__(self,parent=None):
        increase_counter("知乎热点初始化...")

        super(HotTopicsInterface, self).__init__(parent)

    def get_database_name(self) -> str:
        return HotTopicsInterface.DATABASE_NAME

    def get_table_name(self) -> str:
        return HotTopicsInterface.TABLE_NAME

    def get_header_domain_list(self) -> list[ColumnConfig]:
        self.status_mapping = {0: '未使用', 1: '已使用'}
        return [
            ColumnConfig(label="名称", key="topic_name", default_value='', editable=False, op='ct'),
            ColumnConfig(label="内容", key="topic_content", default_value='', editable=False, op='ct'),
            ColumnConfig(label="类型", key="type", default_value='',
                         selectable=True,
                         selectable_list=['微博热点', '抖音热点', '知乎热点'], editable=False),
            ColumnConfig(label="状态", key="status", default_value=0,
                         selectable=True,
                         selectable_list=[{'label': v, 'value': k} for k, v in self.status_mapping.items()],
                         editable=False,
                         display=lambda x, y: self.status_mapping[x]),
            ColumnConfig(label="爬取日期", key="spider_date", default_value=datetime.date.today().strftime("%Y-%m-%d"),
                         editable=False),
            ColumnConfig(label="使用日期", key="use_date", default_value="1000-01-01", editable=False),
            ColumnConfig(label="时间", key="datetime",
                         default_value=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), editable=False,
                         searchable=False),
        ]

    def get_function_button(self) -> list:
        return [
            {"text": "抖音爬虫",
             "icon": MIcon(icons['抖音.svg'], "#FFFFFF"),
             'dayu_type': MPushButton.DefaultType,
             'clicked': self.douyin_spider
             },
            {"text": "微博爬虫",
             "icon": MIcon(icons['新浪微博.svg'], "#FFFFFF"),
             'dayu_type': MPushButton.DefaultType,
             'clicked': self.weibo_spider
             },
            {"text": "Pixabay爬虫",
             "icon": MIcon(icons['pixabay.svg'], "#FFFFFF"),
             'dayu_type': MPushButton.DefaultType,
             'clicked': self.pixabay_spider
             }
        ]

    def douyin_spider(self):
        loop = asyncio.get_running_loop()
        asyncio.run_coroutine_threadsafe(are_you_sure_dialog(parent=self, function=DouyinHotTopicSpider.main_spider),
                                         loop)

    def weibo_spider(self):
        loop = asyncio.get_running_loop()
        asyncio.run_coroutine_threadsafe(are_you_sure_dialog(parent=self, function=WeiboHotTopicSpider.main_spider),
                                         loop)

    def pixabay_spider(self):
        loop = asyncio.get_running_loop()
        asyncio.run_coroutine_threadsafe(are_you_sure_dialog(parent=self, function=PicturePixabaySpider.main_spider),
                                         loop)


if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 创建主循环
    app = QApplication([])
    # 创建异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 创建窗口
    demo_widget = HotTopicsInterface()
    MTheme(theme='dark').apply(demo_widget)
    # 显示窗口
    demo_widget.show()
    loop.run_forever()
