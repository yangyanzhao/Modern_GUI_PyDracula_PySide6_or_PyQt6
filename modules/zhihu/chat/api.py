import asyncio
import datetime
import logging
import os
import random
import re

from modules.gpt_4_free.interface.chat_interface import llm_mapping
from modules.zhihu_auto.chat.default_prompts import mouth_suck_king_prompt
from db.mysql.mysql_jdbc import create_pool, close_pool

except_servers = []


async def chat(pool, prompt, question, timeout: int = 120):
    servers = llm_mapping.values()
    # 除去被限制的模型
    servers = [item for item in servers if item not in except_servers]
    # 打乱顺序
    random.shuffle(servers)
    for server in servers:
        m = server.__name__.strip()
        logging.info(f"正在使用{m}进行发问，请耐心等待")
        meta_result = None
        m_result = await server.chat(pool, prompt, question, timeout)
        meta_result = m_result
        if m_result is None:
            # 如果回答的None，则说明模型被限制了，暂停使用
            logging.info(f"【{m}】回答的None，则说明模型被限制了，暂停使用,切换下一个模型")
            except_servers.append(server)
            continue
        # 对结果进行预处理
        # 有时候回答末尾的emoji识别不出来，要去掉
        if m_result[-8:].startswith("&#"):
            m_result = m_result[:-8]
        if m_result[-9:].startswith("&#"):
            m_result = m_result[:-9]
        if "&#" in m_result:
            m_result = re.sub(r'&#\d+;', '', m_result)
        if m_result.startswith("评论"):
            m_result = m_result[3:]
        # 去掉括号和括号里面的内容
        m_result = re.sub(r'\（.*?\）', '', m_result)
        m_result = re.sub(r'\(.*?\)', '', m_result)
        # 去掉中括号和括号里面的内容
        m_result = re.sub(r'\[.*?\]', '', m_result)
        m_result = re.sub(r'\【.*?\】', '', m_result)
        # 去掉```yuewen与```之间的内容
        m_result = re.sub(r'```yuewen\s*.*?```', '', m_result, flags=re.DOTALL)
        # 去掉“搜索结果”之后的所有内容
        m_result = re.sub(r'搜索结果.*', '', m_result, flags=re.DOTALL)
        m_result = m_result.replace("评论", "")
        m_result = m_result.replace("评价", "")
        m_result = m_result.replace("markdown", "")
        m_result = m_result.replace("**:sweat: ", "")
        m_result = m_result.replace("**:sunglasses:", "")
        m_result = m_result.replace("```json", "").replace("```", "")
        # 有时候#会紧挨着文字，使用正则表达式替换一下
        pattern = r'(?<!\n)(#+)([^\s#])'
        m_result = re.sub(pattern, r'\1 \2', m_result)
        # 有时候-会紧挨着文字，使用正则表达式替换一下
        pattern = r'(?<!\n)(#+)([^\s#])'
        m_result = re.sub(pattern, r'\1 \2', m_result)
        # 有时候|会紧挨着文字，使用正则表达式替换一下
        pattern = r'(\|+)([^\s\|])'
        m_result = re.sub(pattern, r'\1 \2', m_result)
        pattern = r'([^\s\|])(\|+)'
        m_result = re.sub(pattern, r'\1 \2', m_result)

        # 有时候内容会带有图片
        m_result = re.sub(r'!?\[.*?\]\([^)]+\)', '', m_result)
        # 判断是否采纳，是否采纳要进行拆分 TODO，很多回答是合规的，但是被过滤掉了，可以做一个这样的逻辑，回答的问题，如果设计特定的敏感词，可以作为草稿，然后进行人工审核。
        if m_result is None \
                or "抱歉" in m_result[:10] \
                or "会话" in m_result[:10] \
                or "不合规" in m_result[:10] \
                or "不支持" in m_result[:30] \
                or "不可用" in m_result[:30] \
                or "响应错误" in m_result[:30] \
                or "屏蔽" in m_result[:15] \
                or "对不起" in m_result[:10] \
                or "不能" in m_result[:5] \
                or "不理解" in m_result[:10] \
                or "我无法" in m_result[:15] \
                or "I'm sorry" in m_result[:15] \
                or "非法" in m_result[:40] \
                or "违法" in m_result[:40] \
                or "不合法" in m_result[:40] \
                or ("非常" in m_result[:40] and "敏感" in m_result[:40]) \
                or "不道德" in m_result[:40] \
                or "不太确定" in m_result[:40] \
                or "不确定" in m_result[:40] \
                or "模糊" in m_result[:40] \
                or "提问" in m_result[:40] \
                or "敏感" in m_result[:40] \
                or "犯罪" in m_result[:40] \
                or "搜索" in m_result[:40] \
                or "根据" in m_result[:40] \
                or "提供" in m_result[:40] \
                or "让人摸不着头脑" in m_result[:40] \
                or "拒绝回答" in m_result[:40] \
                or "⁇  ⁇  ⁇  ⁇  ⁇  ⁇" in m_result \
                or "error" in m_result \
                or "404" in m_result[:20] \
                or "ai" in m_result \
                or "AI" in m_result \
                or "助手" in m_result \
                or "不能回答" in m_result \
                or "人工智能" in m_result \
                or not bool(re.search('[\u4e00-\u9fff]', m_result)) \
                or m_result.strip() == '':
            logging.info(f"[{m}]模型拒绝回答,将切换为其他模型。处理后：【{m_result}】")
            with open("模型拒绝回答.txt", "a", encoding="utf-8") as f:
                f.write(f"[{m}]模型拒绝回答,将切换为其他模型。处理前：【{meta_result}】\n")
            continue
        return m_result, m
    return None, None


async def main():
    pool = await create_pool(db='zhihu')
    try:
        result, m = await chat(pool=pool, prompt=mouth_suck_king_prompt, question="千秋万古北邙尘?", timeout=60)
        print(m)
        print(result)
    finally:
        await close_pool(pool)


if __name__ == '__main__':
    # 创建日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logs_dir = fr'logs\{datetime.date.today()}'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    # 创建文件处理器，将日志写入文件
    file_handler = logging.FileHandler(
        filename=os.path.join(logs_dir, f'api_{datetime.date.today()}.log'), mode='a',
        encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    # 将处理器添加到日志记录器
    logger.addHandler(file_handler)

    asyncio.run(main())
