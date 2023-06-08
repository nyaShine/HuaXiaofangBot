from botpy import logging

_log = logging.get_logger()


async def direct_message_create_handler(client, message):

    print(message)
