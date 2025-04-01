
from sanic import Sanic
from sanic.log import logger


def task_default(task_id, job_id):
    logger.info("task_default ...")
    pass
