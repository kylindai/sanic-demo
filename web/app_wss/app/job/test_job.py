import asyncio
import gevent

from sanic import Sanic
from sanic.log import logger

from web.app.comm import db, scheduler


def test_task_1(task_id, job_id):
    logger.info("test_task_1 ...")
    # logger.info(scheduler.app.config.JOB_CONFIG['JOBS'][0])
    gevent.sleep(1)
    


async def async_task_1(task_id, job_id):
    logger.info("async_task_1 ...")
    await asyncio.sleep(1)
