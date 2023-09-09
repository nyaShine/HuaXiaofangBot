import asyncio

from botpy import logging

_log = logging.get_logger()


async def run_command(*args):
    process = await asyncio.create_subprocess_exec(*args,
                                                   stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        _log.error(f"命令以错误代码 {process.returncode} 退出")
        _log.error(f"错误信息:\n{stderr.decode()}")
    else:
        _log.info(f"Stdout:\n{stdout.decode()}")
