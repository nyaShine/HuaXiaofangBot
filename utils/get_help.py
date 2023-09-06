import json
import os

from botpy import get_logger
from collections import defaultdict

_log = get_logger()

current_dir = os.path.dirname(os.path.abspath(__file__))
# 构建 botFeatures.json 文件的完整路径
bot_features_path = os.path.join(current_dir, '..', 'config', 'botFeatures.json')

# 读取 botFeature.json 文件并解析成 Python 对象
try:
    with open(bot_features_path, 'r', encoding='utf-8') as f:
        bot_features = json.load(f)
except FileNotFoundError:
    _log.error(f"文件 {bot_features_path} 不存在")
    bot_features = []
except json.JSONDecodeError:
    _log.error(f"文件 {bot_features_path} 不是有效的 JSON 格式")
    bot_features = []

# 将 bot_features 转换为字典，以便快速查找
bot_features_dict = {feature['name']: feature for feature in bot_features}


def get_help(name):
    feature = bot_features_dict.get(name)
    if feature:
        return f"{feature['name']}:\n\n{feature['description']}\n\n使用方法：{feature['usage']}"
    return ""


def get_all_features():
    features_by_category = defaultdict(list)
    for feature in bot_features:
        category = feature.get('category', '其他')
        features_by_category[category].append(feature['name'])
    return features_by_category
