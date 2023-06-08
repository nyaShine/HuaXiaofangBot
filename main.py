import asyncio

from botpy.logging import get_logger
from botpy.forum import Thread
from botpy.message import Message
import botpy

from config import config
from handler.active.active_message_uploader import active_message_uploader
from handler.direct_message.direct_message_create_handler import direct_message_create_handler
from handler.forums.forum_thread_create_handler import forum_thread_create_handler
from handler.forums.forum_thread_update_handler import forum_thread_update_handler
from handler.public_guild_messages.at_message_create_handler import at_message_create_handler
from handler.guild_messages.message_create_handler import message_create_handler

_log = get_logger()


class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    # 当收到@机器人的消息时
    async def on_at_message_create(self, message: Message):
        await at_message_create_handler(self, message)

    # 发送消息事件，代表频道内的全部消息，而不只是 at 机器人的消息
    async def on_message_create(self, message: Message):
        await message_create_handler(self, message)

    # 当收到用户发给机器人的私信消息时
    async def on_direct_message_create(self, message: Message):
        await direct_message_create_handler(self, message)

    # 当用户创建主题时
    async def on_forum_thread_create(self, thread: Thread):
        await forum_thread_create_handler(self, thread)

    # 当用户更新主题时
    async def on_forum_thread_update(self, thread: Thread):
        await forum_thread_update_handler(self, thread)


async def main():
    # 加载 email_verification.db 数据库
    # db = await load_email_verification_database()

    # 订阅所有事件
    intents = botpy.Intents.all()
    client = MyClient(intents=intents)

    # 启动主动消息功能
    asyncio.create_task(active_message_uploader(client))

    await client.start(config["appid"], config["token"])


if __name__ == "__main__":
    asyncio.run(main())
