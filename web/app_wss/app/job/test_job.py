import asyncio

from sanic import Sanic
from sanic.log import logger


def task_test(task_id, job_id):
    logger.info("task_test ...")
    # await asyncio.sleep(1)


async def async_task_test(task_id, job_id):
    logger.info("async_task_test ...")
