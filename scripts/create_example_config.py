import os
import yaml


def create_example_config(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 将敏感信息替换为占位符
    config['appid'] = 'appid'
    config['token'] = 'token'
    config['DHUUsername'] = 'DHUUsername'
    config['DHUPassword'] = 'DHUPassword'
    config['workChannel'] = 'workChannel'

    with open(output_file, 'w') as f:
        yaml.safe_dump(config, f, encoding='GBK', allow_unicode=True)


# 获取当前脚本的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 获取config.yaml文件的路径
config_file = os.path.join(current_dir, '..', 'config.yaml')

# 获取config.yaml.example文件的路径
example_file = os.path.join(current_dir, '..', 'config.yaml.example')

# 注意：这个脚本只用于生成示例配置文件，不应在生产环境中运行。
# 它将敏感信息替换为占位符，从而防止这些信息被泄露。
create_example_config(config_file, example_file)
