from botpy.logging import get_logger
from botpy.message import Message

from utils.encode_urls import encode_urls_in_text

_log = get_logger()


def split_content(content, max_length=1000):
    if not content:
        return [""]
    return [content[i:i + max_length] for i in range(0, len(content), max_length)]


async def post_message_from_event_with_log(client, channel_id, event_id, content, encode_urls=False):
    content = encode_urls_in_text(content, encode_urls)
    contents = split_content(content)

    for content in contents:
        try:
            await client.api.post_message(channel_id=channel_id, event_id=event_id, content=content)
        except Exception as e:
            if 'url not allowed' in str(e):
                content = "所有的.已经被替换为。\n\n" + content.replace(".", "。")
                await client.api.post_message(channel_id=channel_id, event_id=event_id, content=content)
            else:
                _log.error(f"{e}")

        content_escaped_newlines = content.replace('\n', '\\n')
        _log.info(content_escaped_newlines)


async def post_dms_from_message_with_log(client, message: Message, content, encode_urls=False):
    # 创建私信会话
    dms_response = await client.api.create_dms(guild_id=message.guild_id, user_id=message.author.id)
    dms_guild_id = dms_response["guild_id"]
    msg_id = message.id

    try:
        content = encode_urls_in_text(content, encode_urls)

        await client.api.post_dms(
            guild_id=dms_guild_id,
            content=content,
            msg_id=msg_id,
        )

        content_escaped_newlines = content.replace('\n', '\\n')
        _log.info(content_escaped_newlines)

    except Exception as e:
        if 'url not allowed' in str(e):
            content = "所有的.已经被替换为。\n\n" + content.replace(".", "。")
            await client.api.post_dms(
                guild_id=dms_guild_id,
                content=content,
                msg_id=msg_id,
            )
            _log.error(f"URL不允许，已将'.'替换为'。'。Content: {content}")
        else:
            _log.error(f"发送私信失败。异常：{e}")
            _log.error(f"{e}")


async def post_dms_with_log(client, message, content, encode_urls=False):
    try:
        content = encode_urls_in_text(content, encode_urls)

        await client.api.post_dms(
            guild_id=message.guild_id,
            content=content,
            msg_id=message.id,
        )

        content_escaped_newlines = content.replace('\n', '\\n')
        _log.info(content_escaped_newlines)

    except Exception as e:
        if 'url not allowed' in str(e):
            content = "所有的.已经被替换为。\n\n" + content.replace(".", "。")
            await client.api.post_dms(
                guild_id=message.guild_id,
                content=content,
                msg_id=message.id,
            )
            _log.error(f"URL不允许，已将'.'替换为'。'。Content: {content}")
        else:
            _log.error(f"发送私信失败。异常：{e}")
            _log.error(f"{e}")


async def reply_with_log(message, content, quote=True, at=True, encode_urls=False, file_image=None, **kwargs):
    if at:
        content = f"<@{message.author.id}>\n{content}"

    content = encode_urls_in_text(content, encode_urls)

    contents = split_content(content)

    for content in contents:
        if quote:
            message_reference = {"message_id": message.id}
        else:
            message_reference = None
        try:
            await message.reply(content=content, message_reference=message_reference, file_image=file_image, **kwargs)
        except Exception as e:
            if 'url not allowed' in str(e):
                content = "所有的.已经被替换为。\n\n" + content.replace(".", "。")
                await message.reply(content=content, message_reference=message_reference, file_image=file_image,
                                    **kwargs)
            else:
                _log.error(f"{e}")

        content_escaped_newlines = content.replace('\n', '\\n')
        _log.info(content_escaped_newlines)


async def cross_channel_reply_with_log(client, message, content, channel_id, at=True, encode_urls=False, **kwargs):
    if at:
        content = f"<@{message.author.id}> {content}"

    content = encode_urls_in_text(content, encode_urls)

    contents = split_content(content)

    for content in contents:
        try:
            await client.api.post_message(channel_id=channel_id, msg_id=message.id, content=content, **kwargs)
        except Exception as e:
            if 'url not allowed' in str(e):
                content = "所有的.已经被替换为。\n\n" + content.replace(".", "。")
                await client.api.post_message(channel_id=channel_id, msg_id=message.id, content=content, **kwargs)
            else:
                _log.error(f"{e}")

        content_escaped_newlines = content.replace('\n', '\\n')
        _log.info(content_escaped_newlines)


async def post_with_log(client, channel_id, content, encode_urls=False, **kwargs):
    content = encode_urls_in_text(content, encode_urls)

    contents = split_content(content)

    for content in contents:
        message_reference = None
        try:
            await client.api.post_message(channel_id=channel_id, content=content, message_reference=message_reference,
                                          **kwargs)
        except Exception as e:
            if 'url not allowed' in str(e):
                content = "所有的.已经被替换为。\n\n" + content.replace(".", "。")
                await client.api.post_message(channel_id=channel_id, content=content,
                                              message_reference=message_reference, **kwargs)
            else:
                _log.error(f"{e}")

        content_escaped_newlines = content.replace('\n', '\\n')
        _log.info(content_escaped_newlines)
