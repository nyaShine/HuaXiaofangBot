from botpy.logging import get_logger

_log = get_logger()


async def handle_query_identity_group(client, message) -> None:
    # 从消息对象中提取 guildID
    guildID = message.guild_id

    try:
        # 获取频道身份组列表
        response = await client.api.get_guild_roles(guild_id=guildID)
        roles = response['roles']
    except Exception as err:
        _log.error(f"调用 get_guild_roles, err = {err}")
        return

    # 构建包含身份组名称和 ID 的消息
    roleListMsg = "身份组列表：\n"
    for role in roles:
        roleListMsg += f"ID: {role['id']}, 名称: {role['name']}, 人数: {role['number']}, 成员上限: {role['member_limit']}\n"

    _log.info(roleListMsg)
