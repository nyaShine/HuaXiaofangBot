import re
from botpy import logging

from handler.handle_channel_list import handle_channel_list
from handler.handle_help import handle_help
from handler.handle_role import handle_role
from handler.handle_test import handle_test
from utils.send_message_with_log import reply_with_log

_log = logging.get_logger()

COMMANDS = {
    "/帮助": handle_help,
    "/测试": handle_test,
    "/查询身份组": handle_role,
    "/查询子频道": handle_channel_list
}


async def at_message_create_handler(client, message):
    timestamp = message.timestamp
    channel_id = message.channel_id
    member = message.member
    nick = member.nick
    content = message.content

    message_info = f"{timestamp} {channel_id} {nick}: {content}"
    _log.info(message_info)

    command_pattern = re.compile(r"<@!\d+> (/\w+)")
    match = command_pattern.match(content)

    if match:
        param1 = match.group(1)
        handler = COMMANDS.get(param1)
        if handler:
            await handler(client, message)
        else:
            await reply_with_log(message, "无法识别的命令，请检查您的输入。")
    else:
        await reply_with_log(message, "消息格式错误，请使用正确的命令格式。")
