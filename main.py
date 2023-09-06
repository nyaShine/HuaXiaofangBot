import asyncio

from botpy.logging import get_logger
from botpy.message import Message
import botpy
from botpy.user import Member

from config import config
from handler.active.active_message_uploader import active_message_uploader
from handler.guild_members.guild_member_add_handler import guild_member_add_handler
from handler.guild_members.guild_member_update_handler import guild_member_update_handler
from handler.public_guild_messages.at_message_create_handler import at_message_create_handler
from handler.guild_messages.message_create_handler import message_create_handler

_log = get_logger()


class MyClient(botpy.Client):
    def __init__(self, intents):
        # 调用父类的初始化方法，并设置 timeout 为 60
        super().__init__(intents, timeout=60)

    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    # 当收到@机器人的消息时
    async def on_at_message_create(self, message: Message):
        asyncio.create_task(at_message_create_handler(self, message))

    # 发送消息事件，代表频道内的全部消息，而不只是 at 机器人的消息
    async def on_message_create(self, message: Message):
        asyncio.create_task(message_create_handler(self, message))

    # 当成员加入时
    async def on_guild_member_add(self, member: Member):
        asyncio.create_task(guild_member_add_handler(self, member))

    # 当成员资料变更时
    async def on_guild_member_update(self, member: Member):
        asyncio.create_task(guild_member_update_handler(self, member))


async def main():
    # 订阅所有事件
    intents = botpy.Intents.all()
    client = MyClient(intents=intents)

    # 启动主动消息功能
    asyncio.create_task(active_message_uploader(client))

    await client.start(config["appid"], config["token"])


if __name__ == "__main__":
    asyncio.run(main())
