from botpy.logging import get_logger

from utils.roles import is_creator_or_super_admin_from_message
from utils.send_message_with_log import reply_with_log

_log = get_logger()


async def handle_channel_list(client, message) -> None:
    if not is_creator_or_super_admin_from_message(message):
        await reply_with_log(message, "只有频道创建者和超级管理员才能使用该指令。")
        return

    # 从消息对象中提取 guildID
    guildID = message.guild_id

    try:
        # 获取子频道列表
        channels = await client.api.get_channels(guild_id=guildID)
    except Exception as err:
        _log.error(f"调用 get_channels, err = {err}")
        return

    # 构建包含子频道名称和 ID 的消息
    channelListMsg = "子频道列表：\n"
    for channel in channels:
        channelListMsg += f"ID: {channel['id']}, 名称: {channel['name']}\n"

    await reply_with_log(message, channelListMsg)
