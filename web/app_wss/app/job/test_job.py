import asyncio

from sanic import Sanic
from sanic.log import logger

from web.app.comm import db, scheduler


def task_test(task_id, job_id):
    logger.info("task_test ...")
    logger.info(scheduler.app.config.JOB_CONFIG)
    # await asyncio.sleep(1)


async def async_task_test(task_id, job_id):
    logger.info("async_task_test ...")
