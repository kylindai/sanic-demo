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


class Scheduler:

    def __init__(self):
        self._scheduler = AsyncIOScheduler()

    def init_app(self, app: Sanic):
        # logger.error(app.config.DB_CONFIG)
        self._scheduler.configure()
        self._scheduler.start()

    def start(self, app):
        # app.register_listener(self._connect_db, "after_server_start")
        pass

    def shutdown(self):
        # self._scheduler.shutdown()
        pass

    def add_job(self, *args, **kwargs):
        self._scheduler.add_job(*args, **kwargs)

    