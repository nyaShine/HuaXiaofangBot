import json
import re
import os

from utils.get_help import get_help
from utils.send_message_with_log import reply_with_log

# 获取 handle_help.py 文件所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 构建 botFeatures.json 文件的完整路径
bot_features_path = os.path.join(current_dir, '..', 'config', 'botFeatures.json')
# 读取 botFeature.json 文件并解析成 Python 对象
with open(bot_features_path, 'r', encoding='utf-8') as f:
    bot_features = json.load(f)


# 处理帮助命令，向用户返回可用命令的信息。
async def handle_help(client, message):
    content = message.content

    # 使用正则表达式匹配功能名称
    command_pattern = re.compile(r"/帮助\s*(\S*)")
    match = command_pattern.search(content)
    feature_name = ""
    if match:
        feature_name = match.group(1)

    if feature_name:
        # 查找特定功能的帮助信息
        help_msg = get_help(feature_name)
        if not help_msg:
            help_msg = "未找到指定的功能，请检查您的输入。"
    else:
        # 显示所有功能列表
        help_msg = "机器人功能列表：\n\n"
        for i, feature in enumerate(bot_features):
            help_msg += f"{feature['name']}:\n{feature['description']}"
            # 如果当前功能不是最后一个功能，则在描述后添加两个换行符
            if i < len(bot_features) - 1:
                help_msg += "\n\n"

    await reply_with_log(message, help_msg)
