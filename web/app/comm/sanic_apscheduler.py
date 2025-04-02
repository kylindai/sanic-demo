import os
import sys
import copy
import time
import json
import asyncio
import datetime

from typing import Dict, List

from sanic import Sanic
from sanic.log import logger

from contextvars import ContextVar

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


async def async_task_3(task_id, job_id):
    logger.debug("async_task_3 ...")
    await asyncio.sleep(1)


class APScheduler:

    def __init__(self):
        self._scheduler = AsyncIOScheduler()
        self._app = None

    @property
    def app(self) -> Sanic:
        return self._app  # _context.get()

    def init_app(self, app: Sanic):
        # logger.debug(app.config.JOB_CONFIG)
        self._scheduler = AsyncIOScheduler()
        if self._load_config(app) and self._load_job(app):
            self._app = app
            app.register_listener(self._start, "after_server_start")
            app.register_listener(self._shutdown, "before_server_stop")

    def add_job(self, id, func, trigger, **kwargs):
        return self._scheduler.add_job(func=func, trigger=trigger, id=id, **kwargs)

    def remove_job(self, id, jobstore=None):
        self._scheduler.remove_job(id)

    def _load_config(self, app):
        """
        """
        if not app.config.JOB_CONFIG:
            return False

        jobstore = app.config.JOB_CONFIG.get('SCHEDULER_JOBSTORE')
        # table name: apscheduler_jobs
        jobstores = {
            'default': SQLAlchemyJobStore(url=f'sqlite:///{app.config.BASE_DIR}/data/{jobstore}')
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        timezone = 'Asia/Shanghai'
        self._scheduler.configure(job_defaults=job_defaults, timezone=timezone)

        return True

    def _load_job(self, app):
        if app.config.JOB_CONFIG:
            jobs = app.config.JOB_CONFIG.get('JOBS')
            if jobs:
                for job_def in jobs:
                    id = job_def['id']
                    func = job_def['func']
                    trigger = job_def['trigger']['type']
                    kwargs = self._job_kwargs(job_def)
                    # logger.debug(kwargs)
                    self.add_job(id, func, trigger, **kwargs)
        return True

    def _job_kwargs(self, job_def):
        kwargs = copy.copy(job_def)
        kwargs.pop('id')
        kwargs.pop('func')
        trigger = kwargs.pop('trigger')
        trigger.pop('type')
        kwargs |= trigger
        return kwargs

    def _start(self, app, loop):
        self._scheduler.start()
        logger.info("scheduler started")

    def _shutdown(self, app, loop):
        self._scheduler.shutdown()
        logger.info("scheduler shutdown")
