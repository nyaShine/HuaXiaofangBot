import re
from datetime import datetime, timedelta
import json
import os

from botpy import logging
from botpy.errors import ServerError
from botpy.message import Message

from config import config
from utils.send_message_with_log import reply_with_log, cross_channel_reply_with_log

_log = logging.get_logger()


# 定义一个用于管理频道的类
class GuildModeration:
    # 初始化函数，加载规则文件
    def __init__(self):
        self.rules_path = os.path.join("config", "moderation_rules.json")
        self.rules = self.load_rules()
        self.merge_rules_with_defaults()

    # 从文件中加载规则
    def load_rules(self):
        with open(self.rules_path, "r") as f:
            return json.load(f)

    # 合并默认规则和自定义规则
    @staticmethod
    def merge_rules(default_rules, custom_rules):
        for rule in custom_rules:
            for key, value in default_rules.items():
                if key not in rule:
                    rule[key] = value  # 如果自定义规则中缺少某个键，则使用默认值
        return custom_rules

    # 使用默认规则合并消息和用户名规则
    def merge_rules_with_defaults(self):
        default_message_rules = config["moderation_rules"]["default_message_rules"]
        default_username_rules = config["moderation_rules"]["default_username_rules"]
        self.rules["message_rules"] = self.merge_rules(default_message_rules, self.rules["message_rules"])
        self.rules["username_rules"] = self.merge_rules(default_username_rules, self.rules["username_rules"])

    # 执行规则
    @staticmethod
    def execute_rule(rule, match, revoke, remove, remove_and_ban, mute, remove_and_revoke,
                     reminder_channel, reminder_text):
        if match:
            if rule["revoke"]:
                revoke = True
            if rule["remove"]:
                remove = True
            if rule["remove_and_ban"]:
                remove_and_ban = True
            if rule["mute"] > mute:
                mute = rule["mute"]
            if rule["remove_and_revoke"] == -1 or rule["remove_and_revoke"] > remove_and_revoke:
                remove_and_revoke = rule["remove_and_revoke"]
            if not reminder_channel:
                reminder_channel = rule["reminder_channel"]
            reminder_text += rule["reminder_text"]

        return revoke, remove, remove_and_ban, mute, remove_and_revoke, reminder_channel, reminder_text

    # 处理接收到的消息
    async def handle_message(self, client, message: Message):
        revoke = False
        remove = False
        remove_and_ban = False
        mute = 0
        remove_and_revoke = 0
        reminder_channel = ""
        reminder_text = ""
        content = message.content if message.content else ""
        for rule in self.rules["message_rules"]:
            if rule["enabled"]:
                # 如果规则启用，检查消息是否匹配规则
                if rule["exact_match"]:
                    match = any(word == content for word in rule["match_list"])
                elif rule["regex"]:
                    match = any(re.search(pattern, content) for pattern in rule["match_list"])
                else:
                    match = any(word in content for word in rule["match_list"])

                # 检查用户身份组和子频道是否在白名单或黑名单中
                if rule["group_whitelist"]:
                    group_check = any(group in message.member.roles for group in rule["group_list"])
                else:
                    group_check = not any(group in message.member.roles for group in rule["group_list"])

                if rule["channel_whitelist"]:
                    channel_check = message.channel_id in rule["channel_list"]
                else:
                    channel_check = message.channel_id not in rule["channel_list"]

                revoke, remove, remove_and_ban, mute, remove_and_revoke, reminder_channel, reminder_text = \
                    self.execute_rule(rule, match and not group_check and not channel_check, revoke, remove,
                                      remove_and_ban, mute, remove_and_revoke, reminder_channel, reminder_text)

        for rule in self.rules["username_rules"]:
            if rule["enabled"]:
                # 如果规则启用，检查用户名是否匹配规则
                if rule["exact_match"]:
                    match = any(word == message.member.nick for word in rule["match_list"])
                elif rule["regex"]:
                    match = re.search(rule["match_list"], message.member.nick)
                else:
                    match = any(word in message.member.nick for word in rule["match_list"])

                # 检查用户身份组是否在白名单或黑名单中
                if rule["group_whitelist"]:
                    group_check = any(group in message.member.roles for group in rule["group_list"])
                else:
                    group_check = not any(group in message.member.roles for group in rule["group_list"])

                # 如果用户名匹配规则，并且用户身份组通过检查，执行相应的操作
                revoke, remove, remove_and_ban, mute, remove_and_revoke, reminder_channel, reminder_text = \
                    self.execute_rule(rule, match and not group_check, revoke, remove, remove_and_ban, mute,
                                      remove_and_revoke, reminder_channel, reminder_text)

        # 执行最重的处罚
        if revoke:
            try:
                await client.api.recall_message(channel_id=message.channel_id, message_id=message.id,
                                                hidetip=False)
                reminder_text += '已删除包含屏蔽词的消息。'
            except ServerError as e:
                if 'no permission to delete message' in str(e):
                    reminder_text += '无法删除包含屏蔽词的消息。'
                else:
                    _log.error(f'删除消息时发生错误：{e}')

        if mute > 0:
            mute_end_timestamp = int((datetime.now() + timedelta(seconds=mute)).timestamp())
            try:
                await client.api.mute_member(guild_id=message.guild_id, user_id=message.author.id,
                                             mute_end_timestamp=mute_end_timestamp)
                reminder_text += f'已禁言用户，禁言时长为{mute}秒。'
            except ServerError as e:
                if 'oidb rpc call failed' in str(e):
                    reminder_text += '无法禁言发送违禁词的成员。'
                else:
                    _log.error(f'禁言成员时发生错误：{e}')

        if remove:
            try:
                await client.api.get_delete_member(
                    guild_id=message.guild_id,
                    user_id=message.author.id,
                    add_blacklist=remove_and_ban,
                    delete_history_msg_days=remove_and_revoke
                )
                reminder_text += f'已移除用户{"并已拉黑" if remove_and_ban else ""}，并已撤回{"全部历史消息" if remove_and_revoke == -1 else f"过去{remove_and_revoke}天的"}消息。'
            except ServerError as e:
                if 'no privilege remove member' in str(e):
                    reminder_text += '无法移除发送违禁词的成员。'
                else:
                    _log.error(f'移除成员时发生错误：{e}')

        # 发送提醒
        if reminder_channel and reminder_text:
            if reminder_channel == "0":
                # 在同一个channel发送提醒
                await reply_with_log(message, content=reminder_text, quote=False, at=True)
            else:
                # 在不同的channel发送提醒
                await cross_channel_reply_with_log(client, message, content=reminder_text,
                                                   channel_id=reminder_channel, at=True)

    # 当新成员加入或成员资料变更时，检查其用户名
    async def handle_guild_member(self, client, member):
        remove = False
        remove_and_ban = False
        mute = 0
        remove_and_revoke = 0
        for rule in self.rules["username_rules"]:
            if rule["enabled"]:
                # 如果规则启用，检查用户名是否匹配规则
                if rule["exact_match"]:
                    match = any(word == member.nick for word in rule["match_list"])
                elif rule["regex"]:
                    match = re.search(rule["match_list"], member.nick)
                else:
                    match = any(word in member.nick for word in rule["match_list"])

                # 检查用户身份组是否在白名单或黑名单中
                if rule["group_whitelist"]:
                    group_check = any(group in member.roles for group in rule["group_list"])
                else:
                    group_check = not any(group in member.roles for group in rule["group_list"])

                # 如果用户名匹配规则，并且用户身份组通过检查，执行相应的操作
                _, remove, remove_and_ban, mute, remove_and_revoke, _, _ = \
                    self.execute_rule(rule, match and not group_check, False, remove, remove_and_ban, mute,
                                      remove_and_revoke, "", "")

        # 执行最重的处罚
        if mute > 0:
            mute_end_timestamp = int((datetime.now() + timedelta(seconds=mute)).timestamp())
            try:
                await client.api.mute_member(guild_id=member.guild_id, user_id=member.id,
                                             mute_end_timestamp=mute_end_timestamp)
            except ServerError as e:
                if 'oidb rpc call failed' in str(e):
                    _log.error('无法禁言新成员')
                else:
                    _log.error(f'禁言新成员时发生错误：{e}')

        if remove:
            try:
                await client.api.get_delete_member(
                    guild_id=member.guild_id,
                    user_id=member.id,
                    add_blacklist=remove_and_ban,
                    delete_history_msg_days=remove_and_revoke
                )
            except ServerError as e:
                if 'no privilege remove member' in str(e):
                    _log.error('无法移除新成员')
                else:
                    _log.error(f'移除新成员时发生错误：{e}')


guild_moderation = GuildModeration()
