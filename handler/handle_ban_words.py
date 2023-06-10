import re
from datetime import datetime, timedelta
import json

from botpy.errors import ServerError

from config import config
from utils.send_message_with_log import cross_channel_reply_with_log


class BanWordConfig:
    def __init__(self, id: int, enabled: bool, notify: bool, muteTime: int, deleteUser: bool, words: list):
        self.id = id
        self.enabled = enabled
        self.notify = notify
        self.muteTime = muteTime
        self.deleteUser = deleteUser
        self.words = words


def load_ban_words(filename: str) -> list[BanWordConfig]:
    ban_configs = []

    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

        for config in data["configurations"]:
            ban_configs.append(BanWordConfig(
                config["id"],
                config["enabled"],
                config["notify"],
                config["muteTime"],
                config["deleteUser"],
                config["words"]
            ))

    return ban_configs


ban_words_configs = load_ban_words("config/banWords.json")


def find_matching_configuration(message_content: str, ban_words_config: list[BanWordConfig]) -> BanWordConfig:
    for configuration in ban_words_config:
        if not configuration.enabled:
            continue
        for word in configuration.words:
            if re.search(word, message_content):
                return configuration
    return None


async def handle_ban_words(client, message):
    ban_config = find_matching_configuration(message.content, ban_words_configs)
    if ban_config is not None:
        await apply_configuration(client, message, ban_words_configs)


def find_matching_configuration(message_content, ban_words_config):
    for configuration in ban_words_config:
        if not configuration.enabled:
            continue
        for word in configuration.words:
            if re.search(word, message_content):
                return configuration
    return None


async def apply_configuration(client, message, ban_word_configs):
    warning_channel_id = config['warningChannel']
    ban_config = find_matching_configuration(message.content, ban_word_configs)
    if ban_config is not None:
        if ban_config.notify:
            now = datetime.now()
            if 23 <= now.hour or now.hour < 6:
                return
            actions = []
            if ban_config.muteTime > 0:
                actions.append(f'您将被禁言 {ban_config.muteTime} 秒')
            if ban_config.deleteUser:
                actions.append('您将被移出群组')

        if ban_config.muteTime > 0:
            mute_end_timestamp = int(datetime.timestamp(datetime.now() + timedelta(seconds=ban_config.muteTime)))
            try:
                await client.api.mute_member(guild_id=message.guild_id, user_id=message.author.id,
                                             mute_end_timestamp=mute_end_timestamp)
            except ServerError as e:
                if 'oidb rpc call failed' in str(e):
                    # 添加以下代码发送提醒
                    actions.append(f'无法禁言发送违禁词的成员')
                else:
                    raise e

            try:
                await client.api.recall_message(channel_id=message.channel_id, message_id=message.id, hidetip=False)
            except ServerError as e:
                if 'no permission to delete message' in str(e):
                    # 添加以下代码发送提醒
                    actions.append(f'无法删除包含违禁词的消息')
                else:
                    raise e

        if ban_config.deleteUser:
            try:
                await client.api.get_delete_member(
                    guild_id=message.guild_id,
                    user_id=message.author.id,
                    add_blacklist=False,
                    delete_history_msg_days=3
                )
            except ServerError as e:
                if 'no privilege remove member' in str(e):
                    actions.append('无法移除发送违禁词的成员')
                else:
                    raise e

    action_str = '，'.join(actions)
    content = f'您的消息中含有违禁词，请注意！处理方式：{action_str}'
    await cross_channel_reply_with_log(client, message, content, channel_id=warning_channel_id, at=True)
