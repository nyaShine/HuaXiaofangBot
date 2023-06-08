def is_creator(user_roles):
    return '4' in user_roles


def is_creator_from_message(message):
    user_roles = message.member.roles  # 从 Message 对象获取用户的身份组 ID 列表
    print(user_roles)
    return is_creator(user_roles)
