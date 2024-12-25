"""
微博热点爬虫
2024年9月22日21:49:45 调试通过
"""
import asyncio
import datetime
import json
import logging
import os
import traceback

import aiohttp

from db.mysql.mysql_jdbc import select_count, insert_batch, create_pool


class DouyinHotTopicSpider:
    def __init__(self, pool):
        # 直接从GitHub上拉取，不需浏览器，直接程序爬取即可。
        self.url = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/"
        # 多线程中每个线程都要创建一个数据库连接。
        self.pool = pool

    async def run(self):
        logging.info("抖音热点爬虫开始")
        try:
            payload = {}
            headers = {
                'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, headers=headers, data=payload, timeout=30) as response:
                    text = await response.text()
                    loads = json.loads(text)
                    word_list = loads['word_list']
                    word_list.reverse()
                    # 存入数据库
                    data_list = []
                    for word in word_list:
                        content = word['word']
                        count = await select_count(pool=self.pool, table_name='hot_topics',
                                                   condition=[{'field': 'topic_name', 'value': content, 'op': 'eq'},
                                                              {'field': 'status', 'value': 0, 'op': 'eq'}])

                        if count == 0:
                            # TODO 这里应该要对热点去搜索一下相关的热点内容。而不是简简单单的标题。
                            d = {
                                'topic_name': str(content),
                                'topic_content': "",
                                'type': "抖音热点",
                                'status': 0,
                                'spider_date': datetime.date.today(),
                                'use_date': '2000-01-01',
                                'datetime': datetime.datetime.now()
                            }
                            data_list.append(d)
                    if len(data_list) > 0:
                        await insert_batch(pool=self.pool, table_name='hot_topics', data_list=data_list)

                    logging.info("抖音爬虫完毕")
        except asyncio.TimeoutError:
            logging.error("抖音爬虫超时")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            traceback.print_exc()
            exc_info = traceback.format_exc()
            logging.error(exc_info)
        finally:
            pass

    @staticmethod
    async def main_spider():
        # 创建数据库连接池
        pool = await create_pool(db='zhihu')
        try:
            spider = DouyinHotTopicSpider(pool=pool)
            await spider.run()
        finally:
            pool.close()  # 手动关闭连接
            await pool.wait_closed()  # 等待连接关闭


if __name__ == '__main__':
    import nest_asyncio

    # 创建日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logs_dir = fr'logs\{datetime.date.today()}'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    # 创建文件处理器，将日志写入文件
    file_handler = logging.FileHandler(
        filename=os.path.join(logs_dir, f'weibo_hot_topic_spider_{datetime.date.today()}.log'), mode='a',
        encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    # 创建控制台处理器，将日志输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    # 将处理器添加到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    nest_asyncio.apply()  # 允许事件循环嵌套

    asyncio.run(DouyinHotTopicSpider.main_spider())
