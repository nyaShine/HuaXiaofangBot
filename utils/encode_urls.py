import re
import urllib.parse


def encode_urls_in_text(content):
    url_regex = re.compile(
        r'(https?:\/\/)?(([0-9a-z.]+\.[a-z]+)|(([0-9]{1,3}\.){3}[0-9]{1,3}))(:[0-9]+)?(\/[0-9a-z%\/.\-_]*)?(\?[0-9a-z=&%_\-]*)?(\#[0-9a-z=&%_\-]*)?')
    urls = url_regex.finditer(content)

    for url_match in urls:
        url = url_match.group(0)
        encoded_url = urllib.parse.quote(url, safe='')
        final_url = f"https://dhu-1307314281.cos-website.ap-shanghai.myqcloud.com/redirect?target={encoded_url}"
        content = content.replace(url, final_url)

    return content
