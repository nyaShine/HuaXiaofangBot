from botpy import logging
from botpy.user import Member

from handler.guild_moderation import guild_moderation

_log = logging.get_logger()


async def guild_member_add_handler(client, member: Member):
    await guild_moderation.handle_guild_member(client, member)
