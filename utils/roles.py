def is_bot_admin(user_roles):
    return '4' in user_roles


def is_bot_admin_from_message(message):
    user_roles = message.member.roles  # 从 Message 对象获取用户的身份组 ID 列表
    return is_bot_admin(user_roles)


def is_creator_or_super_admin(user_roles):
    return '4' in user_roles or '2' in user_roles


def is_creator_or_super_admin_from_message(message):
    user_roles = message.member.roles  # 从 Message 对象获取用户的身份组 ID 列表
    return is_creator_or_super_admin(user_roles)
