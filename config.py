import os
from ruamel.yaml import YAML

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)  # This line is optional, it sets the indentation style for the output


def read_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, 'r', encoding='utf-8') as config_file:
        return yaml.load(config_file)


def write_config(config_data):
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, 'w', encoding='utf-8') as config_file:
        yaml.dump(config_data, config_file)


config = read_config()
