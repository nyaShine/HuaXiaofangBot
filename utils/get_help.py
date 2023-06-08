import json
import os

# 获取 handle_help.py 文件所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 构建 botFeatures.json 文件的完整路径
bot_features_path = os.path.join(current_dir, '..', 'config', 'botFeatures.json')
# 读取 botFeature.json 文件并解析成 Python 对象
with open(bot_features_path, 'r', encoding='utf-8') as f:
    bot_features = json.load(f)


def get_help(name):
    for feature in bot_features:
        if feature['name'] == name:
            return f"{feature['name']}:\n\n{feature['description']}\n\n使用方法：{feature['usage']}"
    return ""
