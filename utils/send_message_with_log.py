from botpy.errors import ServerError
from botpy.logging import get_logger
from utils.encode_urls import encode_urls_in_text

_log = get_logger()


def split_content(content, max_length=1000):
    return [content[i:i + max_length] for i in range(0, len(content), max_length)]


async def reply_with_log(message, content, quote=True, at=True, encode_urls=False):
    if at:
        content = f"<@{message.author.id}> {content}"

    if encode_urls:
        content = encode_urls_in_text(content)

    contents = split_content(content)

    for content in contents:
        try:
            if quote:
                message_reference = {"message_id": message.id}
            else:
                message_reference = None

            await message.reply(content=content, message_reference=message_reference)
        except ServerError as e:
            if 'url not allowed' in str(e):
                content = "所有的.已经被替换为。\n\n" + content.replace(".", "。")
                await message.reply(content=content, message_reference=message_reference)
            else:
                raise e

        content_escaped_newlines = content.replace('\n', '\\n')
        _log.info(content_escaped_newlines)


async def post_with_log(client, channel_id, content, encode_urls=False):
    if encode_urls:
        content = encode_urls_in_text(content)

    contents = split_content(content)

    for content in contents:
        try:
            message_reference = None
            await client.api.post_message(channel_id=channel_id, content=content, message_reference=message_reference)
        except ServerError as e:
            if 'url not allowed' in str(e):
                content = "所有的.已经被替换为。\n\n" + content.replace(".", "。")
                await client.api.post_message(channel_id=channel_id, content=content,
                                              message_reference=message_reference)
            else:
                raise e

        content_escaped_newlines = content.replace('\n', '\\n')
        _log.info(content_escaped_newlines)
