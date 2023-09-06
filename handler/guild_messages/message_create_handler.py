from botpy import logging

from handler.guild_moderation import guild_moderation

_log = logging.get_logger()


async def message_create_handler(client, message):
    timestamp = message.timestamp
    channel_id = message.channel_id
    member = message.member
    nick = member.nick
    content = message.content

    message_info = f"{timestamp} {channel_id} {nick}: {content}"
    _log.info(message_info)

    await guild_moderation.handle_message(client, message)
