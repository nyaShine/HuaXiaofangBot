import re
from botpy import logging

from handler.handle_chatgpt import handle_chatgpt
from handler.handle_help import handle_help
from handler.handle_query_identity_group import handle_query_identity_group
from handler.handle_query_subchannel import handle_query_subchannel
from handler.handle_question import handle_question
from handler.handle_rss_subscription import handle_rss_subscription
from utils.send_message_with_log import reply_with_log

_log = logging.get_logger()


async def at_message_create_handler(client, message):
    timestamp = message.timestamp
    channel_id = message.channel_id
    member = message.member
    nick = member.nick
    content = message.content

    message_info = f"{timestamp} {channel_id} {nick}: {content}"
    _log.info(message_info)

    # 解析参数1
    command_pattern = re.compile(r"<@!\d+> (/\w+)")
    match = command_pattern.match(content)

    if match:
        param1 = match.group(1)
        if param1 == "/帮助":
            await handle_help(client, message)
        elif param1 == "/问":
            await handle_question(client, message)
        elif param1 == "/c":
            await handle_chatgpt(client, message)
        elif param1 == "/查询子频道":
            await handle_query_subchannel(client, message)
        elif param1 == "/查询身份组":
            await handle_query_identity_group(client, message)
        elif param1 == "/rss订阅":
            await handle_rss_subscription(client, message)
        # elif param1 == "/测试":
        #     await upload_dhu_work(client)
        else:
            await reply_with_log(message, "无法识别的命令，请检查您的输入。")
    else:
        await reply_with_log(message, "消息格式错误，请使用正确的命令格式。")
