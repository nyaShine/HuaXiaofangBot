import re

from botpy.message import Message

from utils.get_help import get_help, get_all_features, bot_features_dict
from utils.send_message_with_log import reply_with_log


def format_features(features):
    if len(features) % 2 == 1:
        features.append("")
    max_length = max(len(feature) for feature in features)
    pairs = zip(features[::2], features[1::2])
    return "\n".join([f"·{convert_to_full_width_char(pair[0]).ljust(max_length).replace(' ', chr(0x3000))}{chr(0x3000)}·{convert_to_full_width_char(pair[1]).ljust(max_length).replace(' ', chr(0x3000))}" if pair[1] else f"·{convert_to_full_width_char(pair[0]).ljust(max_length).replace(' ', chr(0x3000))}" for pair in pairs])


def convert_to_full_width_char(s):
    half_width_char = ''.join(chr(i) for i in range(0x41, 0x5B)) + ''.join(chr(i) for i in range(0x61, 0x7B))
    full_width_char = ''.join(chr(i + 0xFEE0) for i in range(0x41, 0x5B)) + ''.join(chr(i + 0xFEE0) for i in range(0x61, 0x7B))
    trans = str.maketrans(half_width_char, full_width_char)
    return s.translate(trans)


async def handle_help(client, message: Message):
    content = message.content

    command_pattern = re.compile(r"/帮助\s+(/?\S*)")
    match = command_pattern.search(content)
    feature_name = match.group(1) if match else ""

    feature_name = feature_name.lstrip('/')

    usage = bot_features_dict.get("帮助", {}).get("usage", "")

    if feature_name:
        help_msg = get_help(feature_name)
        if not help_msg:
            help_msg = "未找到指定的功能，请检查您的输入。"
    else:
        features_by_category = get_all_features()
        help_msg = f"{usage}\n------------------------------\n机器人功能列表：\n\n"
        for category, features in features_by_category.items():
            formatted_features = format_features(features)
            help_msg += f"{category}:\n" + formatted_features + "\n\n"
        help_msg = help_msg.rstrip('\n')

    await reply_with_log(message, help_msg)
