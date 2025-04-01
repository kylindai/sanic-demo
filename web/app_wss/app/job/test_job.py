
from sanic import Sanic
from sanic.log import logger


def task_default():
    logger.info("task_default ...")
    pass
