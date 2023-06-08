from datetime import datetime

import openai

from botpy.logging import get_logger
from config import config
from utils.send_message_with_log import reply_with_log

_log = get_logger()

# 设置OpenAI的API密钥
openai.api_key = config['OpenAIAPIKey']


# 获取当前时间
def current_time() -> int:
    return int(datetime.now().strftime("%H%M"))


# 检查当前时间是否在配置的工作时间范围内
def is_within_working_hours() -> bool:
    start_time_str, end_time_str = config['enableChatGPTTime'].split('-')
    start_time = datetime.strptime(start_time_str, "%H:%M")
    end_time = datetime.strptime(end_time_str, "%H:%M")
    now = datetime.now().time()

    return start_time.time() <= now < end_time.time()


# 异步调用 GPT-3 API
async def call_gpt3_api(prompt, model_name="gpt-3.5-turbo"):
    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 50
    }
    response = openai.ChatCompletion.create(**data)
    return response


async def handle_chatgpt(client, message):
    # 处理 ChatGPT 命令
    if not config['enableChatGPT'] or not is_within_working_hours():
        await reply_with_log(message, "ChatGPT 功能已禁用或不在工作时间范围内。")
        return

    content = message.content.strip()
    command = "/c "

    # 提取"/c"命令后面的文本
    content = content[len(command):]

    try:
        # 使用 GPT-3 进行单次对话
        response = await call_gpt3_api(content)
        reply_text = response['choices'][0]['message']['content'].strip()

        # 回复消息并记录
        await reply_with_log(message, reply_text)
    except openai.error.RateLimitError as e:
        # 如果触发速率限制，向用户发送提示消息
        await reply_with_log(message, "请求速度过快，已触发速率限制。请1分钟后重试。")
