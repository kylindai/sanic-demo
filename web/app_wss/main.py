import os
import sys
import time
import asyncio

from sanic import Sanic
from sanic.log import logger

from comm.conf.db_conf import Config as db_config

from web.app.comm import db, scheduler, session
from web.app.utils import init_app
from web.app_wss.app.bp import tester
from web.app_wss.conf.job_conf import Config as job_config
#from web.app_wss.conf.session_conf import Config as session_config

async def async_task_2(task_id, job_id):
    logger.debug("async_task_2 ...")
    await asyncio.sleep(1)


def create_app() -> Sanic:
    app = Sanic("APP_WSS")

    app.config.BASE_DIR = os.path.dirname(__file__)
    init_app(app)

    app.register_listener(main_start, "main_process_start")
    app.register_listener(setup_env, "before_server_start")

    return app


async def main_start(app):
    logger.debug("main_start ...")


async def setup_env(app):
    logger.info("setup_env ...")

    # db
    app.config.DB_CONFIG = db_config
    db.init_app(app)

    # scheduler
    app.config.JOB_CONFIG = job_config
    scheduler.init_app(app)

    # session
    app.config.update({
        'SESSION_TYPE': 'filesystem',
        'SESSION_FILE_DIR': f'{app.config.BASE_DIR}/data/sanic_session',
        'SESSION_FILE_THRESHOLD': 1000
    })
    # logger.debug(app.config)
    session.init_app(app, None)
    # session['user_name'] = 'miaowa.pro'

    app.blueprint(tester.bp)
