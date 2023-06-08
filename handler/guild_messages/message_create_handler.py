from botpy import logging

from handler.handle_ban_words import handle_ban_words

_log = logging.get_logger()


async def message_create_handler(client, message):
    timestamp = message.timestamp
    channel_id = message.channel_id
    member = message.member
    nick = member.nick
    content = message.content

    message_info = f"{timestamp} {channel_id} {nick}: {content}"
    _log.info(message_info)

    await handle_ban_words(client, message)
