import os
import yaml


def read_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, 'r', encoding='utf-8') as config_file:
        return yaml.safe_load(config_file)


config = read_config()
