import re

from config import config

# 预编译正则表达式
url_regex = re.compile(
    r'((https?:\/\/)?(([0-9a-zA-Z.-]+\.[a-zA-Z]+)|(([0-9]{1,3}\.){3}[0-9]{1,3}))(:[0-9]+)?(\/[0-9a-zA-Z%\/.\-_]*)?(\?[0-9a-zA-Z=&%_\-]*)?(\#[0-9a-zA-Z=&%_\-]*)?)')


def encode_urls_in_text(content, encode_urls):
    def replace_url(match):
        url = match.group(0)
        preceding_character = content[match.start() - 1] if match.start() > 0 else None
        if preceding_character != '@':
            if encode_urls:
                return config['redirect_url'] + url
            else:
                return url
        else:
            replaced_url = url.replace(".", "。")
            return replaced_url

    replaced_content = url_regex.sub(replace_url, content)
    return replaced_content
