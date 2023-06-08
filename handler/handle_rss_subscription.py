import datetime
import html
import re
import sqlite3
import time

import aiohttp
import feedparser

from config import config, write_config, read_config
from utils.send_message_with_log import reply_with_log, post_with_log
from utils.roles import is_creator_from_message


async def get_rss_subscription(rss_link):
    print(rss_link)
    async with aiohttp.ClientSession() as session:
        async with session.get(rss_link) as response:
            rss_content = await response.text()
            print(rss_content)
            feed = feedparser.parse(rss_content)

    conn = sqlite3.connect("db/rssItems.db")
    cursor = conn.cursor()

    for entry in feed.entries:
        title = entry.title
        link = entry.link
        description = entry.description
        pub_date = time.strftime('%Y-%m-%d %H:%M:%S', entry.published_parsed)  # 将 pub_date 转换为字符串
        guid = entry.guid
        creator = entry.get("creator", "")
        dc_date = entry.get("dc:date", "")
        original_feed_url = rss_link

        cursor.execute("""
            INSERT OR IGNORE INTO rssItems (title, link, description, pub_date, guid, creator, dc_date, is_published, original_feed_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, link, description, pub_date, guid, creator, dc_date, 0, original_feed_url))

    conn.commit()
    conn.close()


async def upload_rss_to_channel(client, channel_id):
    conn = sqlite3.connect("db/rssItems.db")
    cursor = conn.cursor()

    # 从数据库中查找未发布的数据
    cursor.execute("SELECT * FROM rssItems WHERE is_published = 0")
    unpublished_items = cursor.fetchall()

    for item in unpublished_items:
        # 将 pub_date 转换为更易读的格式
        pub_date = datetime.datetime.strptime(item[4], "%Y-%m-%d %H:%M:%S")
        pub_date_str = pub_date.strftime("%Y-%m-%d")

        # 根据实际需求格式化内容
        content = (
            f"东华大学教务处通知公告：\n"
            f"{item[1]} ({pub_date_str})\n"
            f"{item[2]}\n"
            f"{item[3]}"
        )

        # 发送内容
        await post_with_log(client, channel_id, content, encode_urls=True)

        # 更新数据库中的is_published字段
        cursor.execute("UPDATE rssItems SET is_published = 1 WHERE id = ?", (item[0],))

    conn.commit()
    conn.close()


async def upload_rss_subscription(client):
    rssFeeds = config['rssFeeds']
    for rss_link, channel_id in rssFeeds.items():
        await get_rss_subscription(rss_link)
        await upload_rss_to_channel(client, channel_id)


async def handle_rss_subscription(client, message):
    # 检查用户是否具有creator身份组
    print(message)
    print(is_creator_from_message(message))
    if not is_creator_from_message(message):
        await reply_with_log(message, "您没有权限使用此功能。仅限creator身份组的用户可以使用。")
        return
    config = read_config()

    # 从消息中提取 RSS 链接
    rss_url_pattern = r'https?://\S+'
    match = re.search(rss_url_pattern, message.content)
    if match:
        rss_url = html.unescape(match.group(0))  # 使用html.unescape()对URL进行解码
    else:
        await reply_with_log(message, "未找到有效的 RSS 链接。请提供一个有效的 RSS 链接。")
        return

    # 将 RSS 链接添加到配置文件
    if 'rssFeeds' not in config:
        config['rssFeeds'] = {}

    channel_id = message.channel_id

    config['rssFeeds'][rss_url] = str(channel_id)

    # 将更新后的配置写入文件
    write_config(config)

    await reply_with_log(message, f"已成功在子频道 {channel_id} 上添加 RSS 订阅：{rss_url}")
