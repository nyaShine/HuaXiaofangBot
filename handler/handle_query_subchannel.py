from botpy.logging import get_logger

_log = get_logger()


async def handle_query_subchannel(client, message) -> None:
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

    _log.info(channelListMsg)
