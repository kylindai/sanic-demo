import asyncio
import gevent

from sanic import Sanic
from sanic.log import logger
from sqlalchemy import select

from web.app.comm import db, scheduler
from web.app_wss.app.biz.biz_model import SystemConf


def test_task_1(task_id, job_id):
    logger.info(f"test_task_1 ... {task_id}, {job_id}")
    # logger.info(scheduler.app.config.JOB_CONFIG['JOBS'][0])
    gevent.sleep(1)


async def async_task_1(task_id, job_id):
    logger.info(f"async_task_1 ... {task_id}, {job_id}")
    try:
        await asyncio.sleep(1)
        async with db.session() as session:
            stmt = select(SystemConf).where(SystemConf.id == job_id)
            result = await session.execute(stmt)
            system_conf = result.scalar()
            if system_conf:
                logger.debug(system_conf.to_dict())
            else:
                logger.debug("no system_conf found")
    except Exception as e:
        logger.error(e)
