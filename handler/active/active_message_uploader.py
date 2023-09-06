import asyncio
import datetime

from botpy import logging
import aiocron

from handler.handle_dhu_work import upload_dhu_work

_log = logging.get_logger()


def is_time_range_valid():
    now = datetime.datetime.now().time()
    start_time = datetime.time(23, 50)
    end_time = datetime.time(6, 0)

    return not (start_time <= now <= end_time)


async def active_message_uploader(client):
    # 设置每7小时调用一次函数upload_dhu_work()
    @aiocron.crontab('0 */7 * * *')
    async def call_upload_dhu_work():
        if is_time_range_valid():
            asyncio.create_task(upload_dhu_work(client))
        else:
            _log.info("Skipped upload_dhu_work() due to time constraints.")

    # 为了持续运行定时任务，我们需要在这里创建一个永久循环
    while True:
        await asyncio.sleep(60)
