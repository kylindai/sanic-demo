import os
import sys

from sanic import Sanic
from sanic.log import logger

from comm.conf.db_conf import Config as db_config

from web.app.comm import db, scheduler
from web.app.utils import init_app
from web.app_wss.app.bp import tester
from web.app_wss.conf.job_conf import Config as job_config 


def create_app() -> Sanic:
    app = Sanic("APP_WSS")

    app.config.BASE_DIR = os.path.dirname(__file__)
    init_app(app)

    app.register_listener(main_start, "main_process_start")
    app.register_listener(setup_env, "before_server_start")

    # app.register_middleware(convert_to_json, "response")

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

    app.blueprint(tester.bp)
