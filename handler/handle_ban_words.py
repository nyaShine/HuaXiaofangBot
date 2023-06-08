import re
from datetime import datetime, timedelta

from config import config
from config_loader.load_ban_words import load_ban_words, BanWordConfig
from utils.send_message_with_log import post_with_log

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
                actions.append('您将被移出群组并加入黑名单')

            action_str = '，'.join(actions)
            content = f'<@{message.author.id}> 您的消息中含有违禁词，请注意！处理方式：{action_str}'
            await post_with_log(client, warning_channel_id, content)

        if ban_config.muteTime > 0:
            mute_end_timestamp = int(datetime.timestamp(datetime.now() + timedelta(seconds=ban_config.muteTime)))
            await client.api.mute_member(guild_id=message.guild_id, user_id=message.author.id,
                                         mute_end_timestamp=mute_end_timestamp)
            await client.api.recall_message(channel_id=message.channel_id, message_id=message.id, hidetip=False)

        if ban_config.deleteUser:
            await client.api.get_delete_member(
                guild_id=message.guild_id,
                user_id=message.author.id,
                add_blacklist=True,
                delete_history_msg_days=3
            )
