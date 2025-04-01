import os
import sys
import time
import json
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
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


class APScheduler:

    def __init__(self, scheduler=None):
        self._scheduler = scheduler or AsyncIOScheduler()
        self._app = None

    def init_app(self, app: Sanic):
        # logger.debug(app.config.JOB_CONFIG)
        if self._load_config(app) and self._load_job(app):
            self._app = app
            app.register_listener(self.start, "after_server_start")
            app.register_listener(self.shutdown, "before_server_stop")

    def start(self, app, loop):
        if self._app:
            self._scheduler.start()
            logger.info("scheduler started")

    def shutdown(self, app, loop):
        if self._app:
            self._scheduler.shutdown()
            logger.info("scheduler shutdown")

    def configure(self, job_config):
        self._load_config(job_config)

    def add_job(self, id, func, **kwargs):
        job_def = dict(kwargs)
        job_def["id"] = id
        job_def["func"] = func
        job_def["name"] = job_def.get("name") or id
        self._fix_job_def(job_def)

        return self._scheduler.add_job(**job_def)

    def remove_job(self, id, jobstore=None):
        self._scheduler.remove_job(id)

    def _load_config(self, app):
        """
        Load the configuration from the Flask configuration.
        """
        if not app.config.JOB_CONFIG:
            return False

        jobstore = app.config.JOB_CONFIG.get('SCHEDULER_JOBSTORE')
        # table name: apscheduler_jobs
        jobstores = {
            'default': SQLAlchemyJobStore(url=f'sqlite:///{app.config.BASE_DIR}/data/{jobstore}')
        }
        executors = {
            'default': ThreadPoolExecutor(20),
            'processpool': ProcessPoolExecutor(5)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        timezone = 'Asia/Shanghai'
        self._scheduler.configure(#jobstores=jobstores,
                                  executors=executors,
                                  job_defaults=job_defaults,
                                  timezone=timezone)
        """
        options = dict()
        # jobstores
        job_stores = app.config.get("SCHEDULER_JOBSTORES")
        if job_stores:
            options["jobstores"] = job_stores
        # executors
        executors = app.config.get("SCHEDULER_EXECUTORS")
        if executors:
            options["executors"] = executors
        # job defaults
        job_defaults = app.config.get("SCHEDULER_JOB_DEFAULTS")
        if job_defaults:
            options["job_defaults"] = job_defaults
        # timezone
        timezone = app.config.get("SCHEDULER_TIMEZONE")
        if timezone:
            options["timezone"] = timezone
        # configure
        # self._scheduler.configure(**options)
        """

        return True

    def _load_job(self, app):
        if app.config.JOB_CONFIG:
            jobs = app.config.JOB_CONFIG.get('JOBS')
            if jobs:
                for job in jobs:
                    if not self._scheduler.get_job(job.get('id')):
                        self.add_job(**job)
            return True

    def _fix_job_def(self, job_def):
        """
        Replaces the datetime in string by datetime object.
        """
        """
        if isinstance(job_def.get("start_date"), str):
            job_def["start_date"] = dateutil.parser.parse(job_def.get("start_date"))
        if isinstance(job_def.get("end_date"), str):
            job_def["end_date"] = dateutil.parser.parse(job_def.get("end_date"))
        if isinstance(job_def.get("run_date"), str):
            job_def["run_date"] = dateutil.parser.parse(job_def.get("run_date"))
        """

        # it keeps compatibility backward
        if isinstance(job_def.get("trigger"), dict):
            trigger = job_def.pop("trigger")
            job_def["trigger"] = trigger.pop("type", "date")
            job_def.update(trigger)
