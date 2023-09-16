import asyncio
import sqlite3
import time
from typing import Tuple, List, Dict

from botpy import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

from config import config
from utils.run_command import run_command
from utils.send_message_with_log import post_with_log

_log = logging.get_logger()


async def get_dhu_work():
    # 打开 MotionPro
    try:
        await asyncio.wait_for(
            run_command('/opt/MotionPro/vpn_cmdline', '-h', 'vpn.dhu.edu.cn', '-u', str(config['DHUUsername']),
                        '-p', str(config['DHUPassword'])), timeout=30)  # 设置超时时间为30秒
    except asyncio.TimeoutError:
        _log.error("VPN connection timed out.")
        # 关闭 MotionPro
        await run_command('/opt/MotionPro/vpn_cmdline', '-s')
        # 重启 systemd-resolved 服务
        await run_command('sudo', 'systemctl', 'restart', 'systemd-resolved')
        return
    except Exception as e:
        _log.error(f"An error occurred while connecting to VPN: {e}")
        # 关闭 MotionPro
        await run_command('/opt/MotionPro/vpn_cmdline', '-s')
        # 重启 systemd-resolved 服务
        await run_command('sudo', 'systemctl', 'restart', 'systemd-resolved')
        return

    # 设置Chrome选项
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # 初始化webdriver
    driver = webdriver.Chrome(options=options)

    # 打开网站
    driver.get("https://webproxy.dhu.edu.cn")

    # 等待页面加载完成
    time.sleep(5)

    # 输入用户名和密码
    username_input = driver.find_element(By.ID, "username")
    password_input = driver.find_element(By.ID, "password")

    username = config["DHUUsername"]
    password = config["DHUPassword"]

    username_input.send_keys(username)
    password_input.send_keys(password)

    # 点击登录按钮
    login_button = driver.find_element(By.CLASS_NAME, "auth_login_btn")
    login_button.click()

    # 等待登录完成
    time.sleep(10)

    # 登录成功后，先访问学生工作系统网页
    middle_url = "https://webproxy.dhu.edu.cn/https/446a50612140233230323231314468550c2c6d400eaaa52decadbb464a26db7a8014/"
    driver.get(middle_url)

    # 登录成功后，访问目标网页（校外勤工助学信息）
    target_url = "https://webproxy.dhu.edu.cn/http/446a50612140233230323231314468550c2c6d400eaaa52decadbb464a26db7a8014/xg_dhu/s/biz/xwqgzx/gwgl/list?jddes=6fd6afa75cac998360fcd2bd8a6998,B6589FC6AB0DC82CF12099D1C2D40AB994E8410C"
    driver.get(target_url)

    # 等待页面加载完成
    time.sleep(10)

    # 获取网页源代码
    html = driver.page_source
    # _log.debug(f"Website source code: {html}")
    soup = BeautifulSoup(html, 'html.parser')

    # 提取表格数据
    table = soup.find('table')
    table_data = []

    if table:
        for row in table.find_all('tr'):
            columns = row.find_all('td')
            rowData = []

            for column in columns:
                # 如果存在title属性，则获取title属性值，否则获取文本内容
                if column.get('title'):
                    rowData.append(column.get('title').strip())
                else:
                    rowData.append(column.text.strip())

            table_data.append(rowData)
    else:
        _log.error("Table not found.")
        # Handle the case when the table is not found

    # 移除无关的列（第一列和第二列）
    for i in range(len(table_data)):
        table_data[i] = table_data[i][2:]

    # 手动输入列名创建DataFrame
    columns = ['岗位编号', '发布部门', '岗位名称/家教科目', '岗位类型', '预计待遇', '工作时间', '工作地点',
               '困难认定要求', '面向对象', '预报人数限制', '发布状态']
    df1 = pd.DataFrame(table_data[1:], columns=columns)

    target_url2 = "https://webproxy.dhu.edu.cn/https/446a50612140233230323231314468550c2c6d400eaaa52decadbb464a26db7a8014/xg_dhu/s/biz/qgzxGwgl/list?jddes=739cf592e0a909884bc074f0e2d1310c,B6589FC6AB0DC82CF12099D1C2D40AB994E8410C"
    driver.get(target_url2)

    # 等待页面加载完成
    time.sleep(10)

    # 获取网页源代码
    html = driver.page_source
    # _log.debug(f"Website source code: {html}")
    soup = BeautifulSoup(html, 'html.parser')

    # 提取表格数据
    table = soup.find('table')
    table_data = []

    if table:
        for row in table.find_all('tr'):
            columns = row.find_all('td')
            rowData = []

            # 指定需要保留的列索引
            keep_indices = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

            for index, column in enumerate(columns):
                if index in keep_indices:
                    # 如果存在title属性，则获取title属性值，否则获取文本内容
                    if column.get('title'):
                        rowData.append(column.get('title').strip())
                    else:
                        rowData.append(column.text.strip())

            table_data.append(rowData)
    else:
        _log.error("Table not found.")
        # Handle the case when the table is not found

    # 手动输入列名创建DataFrame
    columns = ['操作', '学年', '校区', '用工单位', '岗位名称', '工作地点', '联系人', '联系电话', '招聘人数', '已聘人数',
               '空余岗位']
    df2 = pd.DataFrame(table_data[1:], columns=columns)

    # 最后，关闭浏览器
    driver.quit()

    # 创建一个数据库连接
    connection = sqlite3.connect("db/workInfo.db")

    # 为DataFrame添加新列
    df1['发布在频道'] = '未发布'
    df2['发布在频道'] = '未发布'

    # 检查并导入onCampusWork表数据
    table_exists = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='onCampusWork'").fetchone()
    if table_exists:
        df2_existing = pd.read_sql_query("SELECT * FROM onCampusWork", connection)
        df2_merged = pd.concat([df2_existing, df2]).drop_duplicates(
            subset=['学年', '校区', '用工单位', '岗位名称', '工作地点'],
            keep='first')
    else:
        df2_merged = df2

    df2_merged.to_sql('onCampusWork', connection, if_exists='replace', index=False)

    # 检查并导入offCampusWork表数据
    table_exists = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='offCampusWork'").fetchone()
    if table_exists:
        df1_existing = pd.read_sql_query("SELECT * FROM offCampusWork", connection)
        df1_merged = pd.concat([df1_existing, df1]).drop_duplicates(subset=['岗位编号'], keep='first')
    else:
        df1_merged = df1

    df1_merged.to_sql('offCampusWork', connection, if_exists='replace', index=False)

    # 关闭数据库连接
    connection.close()

    # 关闭 MotionPro
    await run_command('/opt/MotionPro/vpn_cmdline', '-s')

    # 重启 systemd-resolved 服务
    await run_command('sudo', 'systemctl', 'restart', 'systemd-resolved')


async def get_dhu_work_info() -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    conn = sqlite3.connect('db/workInfo.db')
    cursor = conn.cursor()

    on_campus_works = []
    off_campus_works = []

    on_campus_rows = cursor.execute("SELECT * FROM onCampusWork")
    for row in on_campus_rows:
        column_names = [description[0] for description in on_campus_rows.description]
        work = dict(zip(column_names, row))
        on_campus_works.append(work)

    off_campus_rows = cursor.execute("SELECT * FROM offCampusWork")
    for row in off_campus_rows:
        off_campus_column_names = [description[0] for description in off_campus_rows.description]
        work = dict(zip(off_campus_column_names, row))
        off_campus_works.append(work)

    cursor.close()
    conn.close()

    return on_campus_works, off_campus_works


async def update_on_campus_work_status(学年: str, 校区: str, 用工单位: str, 岗位名称: str, 工作地点: str,
                                       status: str) -> None:
    conn = sqlite3.connect('db/workInfo.db')
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE onCampusWork SET 发布在频道 = ? WHERE 学年 = ? AND 校区 = ? AND 用工单位 = ? AND 岗位名称 = ? AND 工作地点 = ?",
        (status, 学年, 校区, 用工单位, 岗位名称, 工作地点))
    conn.commit()

    cursor.close()
    conn.close()


async def update_off_campus_work_status(work_id: str, status: str) -> None:
    conn = sqlite3.connect('db/workInfo.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE offCampusWork SET 发布在频道 = ? WHERE 岗位编号 = ?",
                   (status, work_id))
    conn.commit()

    cursor.close()
    conn.close()


async def upload_dhu_work_to_channel(client) -> None:
    channel_id = config["workChannel"]
    on_campus_works, off_campus_works = await get_dhu_work_info()

    for work in on_campus_works:
        if work["操作"] == "申请工作" and work["发布在频道"] == "未发布":
            message = f"东华大学校内勤工助学信息:\n学年: {work['学年']}\n校区: {work['校区']}\n用工单位: {work['用工单位']}\n岗位名称: {work['岗位名称']}\n工作地点: {work['工作地点']}\n联系人: {work['联系人']}\n联系电话: {work['联系电话']}\n招聘人数: {work['招聘人数']}\n已聘人数: {work['已聘人数']}\n空余岗位: {work['空余岗位']}\n报名方式：\n【网上服务大厅】-【新学生工作管理系统】-【勤工助学】\n注意事项：详情请见【新学生工作管理系统】-【勤工助学】页面"
            await post_with_log(client, channel_id, message)
            await update_on_campus_work_status(work["学年"], work["校区"], work["用工单位"], work["岗位名称"],
                                               work["工作地点"], "已发布")

    for work in off_campus_works:
        if work["发布在频道"] == "未发布":
            message = f"东华大学校外勤工助学信息:\n岗位编号: {work['岗位编号']}\n发布部门: {work['发布部门']}\n岗位名称/家教科目: {work['岗位名称/家教科目']}\n岗位类型: {work['岗位类型']}\n预计待遇: {work['预计待遇']}\n工作时间: {work['工作时间']}\n工作地点: {work['工作地点']}\n困难认定要求: {work['困难认定要求']}\n面向对象: {work['面向对象']}\n预报人数限制: {work['预报人数限制']}\n报名方式：\n【企业微信】-【工作台】-【校务管理类】-【新学工系统】-【校外勤工助学】\n【网上服务大厅】-【新学生工作管理系统】-【校外勤工助学】\n注意事项：若在【企业微信】未看到此业务，则报名人数已满\n详情请见【新学生工作管理系统】-【勤工助学】页面"
            await post_with_log(client, channel_id, message)
            await update_off_campus_work_status(work["岗位编号"], "已发布")


async def upload_dhu_work(client):
    try:
        await get_dhu_work()
    except Exception as e:
        _log.error(f"An error occurred while getting DHU work: {e}")
    await upload_dhu_work_to_channel(client)
