import os
import sys
import time
import asyncio

from sanic import Sanic
from sanic.log import logger

from comm.conf.db_conf import Config as db_config

from web.app.ext import db, session, static, template, login_manager, scheduler
from web.app.utils import init_app
from web.app_wss.app.bp import tester
from web.app_wss.conf import app_config, session_config, login_config, job_config


async def async_task_2(task_id, job_id):
    logger.debug("async_task_2 ...")
    await asyncio.sleep(1)


def create_app() -> Sanic:
    app = Sanic("APP_WSS")

    app.config.BASE_DIR = os.path.dirname(__file__)
    app.config.update(app_config)
    init_app(app)

    app.register_listener(main_start, "main_process_start")
    app.register_listener(server_setup, "before_server_start")

    return app


async def main_start(app):
    logger.debug("main_start ...")


async def server_setup(app):
    logger.info("server_setup ...")

    # db
    app.config.DB_CONFIG = db_config
    db.init_app(app)

    # session
    app.config.SESSION_CONFIG = session_config
    session.init_app(app)

    # static & template
    app.config.BASE_DIR = os.path.dirname(__file__)
    static.init_app(app)
    template.init_app(app)

    # login_manager
    app.config.LOGIN_CONFIG = login_config
    login_manager.init_app(app)

    # scheduler
    app.config.JOB_CONFIG = job_config
    scheduler.init_app(app)


    # blueprint
    app.blueprint(tester.bp)
