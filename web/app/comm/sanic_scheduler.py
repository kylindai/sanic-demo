import os
import sys
import time
import json
import datetime

from typing import Dict, List

from sanic import Sanic
from sanic.log import logger

from contextvars import ContextVar
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger


class Scheduler:

    def __init__(self):
        self._scheduler = AsyncIOScheduler()
        self._app = None

    def init_app(self, app: Sanic):
        # logger.error(app.config.DB_CONFIG)
        if self._scheduler.configure(app):
            self._app = app
            app.register_listener(self.start, "after_server_start")
            app.register_listener(self.shutdown, "before_server_stop")

    def configure(self, app):
        if app.config.JOB_CONFIG:
            jobs = app.config.JOB_CONFIG['JOBS']
            if jobs:
                for job in jobs:
                    self._scheduler.add_job(
                        id=job['id'],
                        trigger=IntervalTrigger(seconds=10),
                        func=job['func'],
                        args=job['args']
                    )
                return True

    def start(self, app, loop):
        # app.register_listener(self._connect_db, "after_server_start")
        if self._app:
            self._scheduler.start()
            logger.info("scheduler started")

    def shutdown(self, app, loop):
        if self._app:
            self._scheduler.shutdown()
            logger.info("scheduler shutdown")

    def add_job(self, *args, **kwargs):
        self._scheduler.add_job(*args, **kwargs)
