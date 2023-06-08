import os
import sqlite3
from datetime import datetime

from config import config, write_config
from utils.get_help import get_help
from utils.send_message_with_log import reply_with_log
from utils.roles import is_creator_from_message


def connect_to_db():
    # 获取当前文件的绝对路径
    current_file_path = os.path.abspath(__file__)
    # 获取项目根目录路径
    project_root_path = os.path.dirname(os.path.dirname(current_file_path))
    # 构建数据库文件的相对路径
    db_relative_path = os.path.join(project_root_path, "db", "questionAnswer.db")
    # 连接到数据库
    conn = sqlite3.connect(db_relative_path)
    return conn


def split_keywords(keywords):
    return [keyword.strip() for keyword in keywords.split(',')]


# 根据问题和答案搜索
def search_questions(keywords, smart_search=False):
    keywords_list = split_keywords(keywords)
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        current_date = datetime.now().strftime('%Y-%m-%d')
        query_conditions = " AND ".join(
            [f"(question LIKE '%{keyword}%' OR answer LIKE '%{keyword}%')" for keyword in keywords_list])

        # 根据问题名和答案内容搜索
        cursor.execute(f"""
            SELECT id, question, answer, alias FROM questionAnswer
            WHERE {query_conditions} AND (end_date > ? OR end_date IS NULL OR end_date = '')
        """, (current_date,))
        results = cursor.fetchall()

        conn.close()
    except sqlite3.Error as e:
        print("Error: ", e)

    if smart_search and len(results) == 1:
        return results[0]  # 返回问题的ID，问题，别名和答案
    else:
        return results


# 将问答添加到数据库
def add_question_answer(question, answer, alias=None):
    conn = connect_to_db()
    cursor = conn.cursor()
    added_date = datetime.now().strftime('%Y-%m-%d')

    # 检查问题是否已经存在
    cursor.execute("""
        SELECT COUNT(*) FROM questionAnswer WHERE question = ?
    """, (question,))
    count = cursor.fetchone()[0]
    if count > 0:
        print("问题已存在。")
        return False

    try:
        cursor.execute("""
            INSERT INTO questionAnswer (question, answer, alias, added_date)
            VALUES (?, ?, ?, ?)
        """, (question, answer, alias, added_date))

        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print("Error: ", e)
        return False


# 将子频道添加到config/config.yaml中的别名搜索白名单中
def add_channel_to_alias_whitelist(message):
    if is_creator_from_message(message):
        if config['aliasSearchWhitelist']:
            channels = [int(channel.strip()) for channel in config['aliasSearchWhitelist'].split(',')]
        else:
            channels = []

        # 如果子频道不在白名单中，将其添加到白名单
        if message.channel_id not in channels:
            channels.append(message.channel_id)
            # 将整数列表转换为逗号分隔的字符串
            config['aliasSearchWhitelist'] = ','.join([str(channel) for channel in channels])
            write_config(config)
            return True
        else:
            return False  # 子频道已在白名单中


# 提交错误报告
async def report_error(client, message):
    content = message.content.strip()
    command_parts = content.split(" ")

    if len(command_parts) < 5:
        response = "使用方式: @机器人 /问 报错 ID 报错文本"
        return response

    error_id = command_parts[3]
    error_text = " ".join(command_parts[4:])

    if not error_id.isdigit():
        response = "错误: ID 必须是一个数字。"
        return response

    error_id = int(error_id)

    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        # 获取当前的 error_message
        cursor.execute("""
            SELECT error_message FROM questionAnswer WHERE id = ?
        """, (error_id,))
        current_error_message = cursor.fetchone()[0]

        # 更新 error_message
        if current_error_message:
            new_error_message = current_error_message + "**********" + error_text
        else:
            new_error_message = error_text

        cursor.execute("""
            UPDATE questionAnswer SET error_message = ? WHERE id = ?
        """, (new_error_message, error_id))

        conn.commit()
        conn.close()

        response = "错误报告已提交，感谢您的反馈！"
    except sqlite3.Error as e:
        print("Error: ", e)
        response = "提交错误报告时发生错误。"
    return response


# 实现多关键词匹配问题的智能搜索
def smart_search(keywords):
    # 检查关键字是否为数字
    if keywords.isdigit():
        conn = connect_to_db()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, question, answer, alias FROM questionAnswer
                WHERE id = ?
            """, (int(keywords),))
            result = cursor.fetchone()
            conn.close()
        except sqlite3.Error as e:
            print("Error: ", e)

        # 如果找到了匹配的问题，返回问题的 ID，问题，别名和答案
        if result:
            id, question, answer, alias = result
            # 将答案中的 "\\n" 替换为换行符
            answer = answer.replace("\\n", "\n")
            question_with_alias = f"{question} ({alias})" if alias else question

            return id, question_with_alias, answer
        else:
            return None

    else:
        result = search_questions(keywords, smart_search=True)

        if isinstance(result, tuple):
            id, question, answer, alias = result
            # 将答案中的 "\\n" 替换为换行符
            answer = answer.replace("\\n", "\n")

            question_with_alias = f"{question} ({alias})" if alias and alias.strip() else question

            return id, question_with_alias, answer

        else:
            # 如果找到了多个结果，返回结果列表
            return result


async def handle_question(client, message):
    content = message.content.strip()
    command_parts = content.split(" ")

    if len(command_parts) < 3:
        await reply_with_log(message, get_help("/问"))
        return

    action = command_parts[2]
    args = " ".join(command_parts[3:])

    if action == "添加问答":
        question_answer_parts = args.split(':', 1)
        if len(question_answer_parts) == 2:
            question, answer = question_answer_parts
            alias = None
            if '(' in question:
                question_parts = question.split('(', 1)
                question = question_parts[0].strip()
                alias = question_parts[1].strip().rstrip(')')
            success = add_question_answer(question, answer, alias)
            if success:
                response = "问题和答案已成功添加到数据库。"
            else:
                response = "添加问题和答案时发生错误。可能是问题已存在。"
    elif action == "添加到别名白名单":
        success = add_channel_to_alias_whitelist(message)
        if success:
            response = "子频道已成功添加到别名搜索白名单。"
        elif success is None:
            response = "你没有添加权限，或子频道已经在别名搜索白名单中。"
        else:
            response = "添加子频道到别名白名单时发生错误。"
    elif action == "报错":
        response = await report_error(client, message)
    else:
        search_result = smart_search(action)

        if isinstance(search_result, tuple):
            id, question_with_alias, answer = search_result
            response = f"{id} - {question_with_alias}\n\n{answer}"
        elif search_result:  # 如果 search_result 是一个非空列表
            response = "\n\n".join([f"{result[0]} - {result[1]} ({result[3]})" if result[3] and result[
                3].strip() else f"{result[0]} - {result[1]}" for result in search_result])
        else:  # 如果 search_result 为空，表示没有匹配的结果
            response = "抱歉，没有找到与您的搜索关键词匹配的结果。"

    await reply_with_log(message, response, encode_urls=True)  # 发送响应
