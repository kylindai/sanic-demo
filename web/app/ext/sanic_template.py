import os
import sys
import time

from typing import Dict, List

from sanic import Sanic
from sanic.log import logger, Colors
from sanic.request import Request
from jinja2.runtime import Context
from jinja2.utils import missing

from web.app.utils.utils_html import eval, format_data

from .sanic_session import SanicSession


class SanicTemplateContext(Context):
    def resolve_or_missing(self, key: str):
        rv = super().resolve_or_missing(key)
        logger.debug(f"{Colors.RED}KEY = {key}, value={rv}{Colors.END}")
        # session var ressolve
        if key == 'session':
            logger.debug(f"{type(rv)}")
            pass
        return rv


class SanicTemplate:

    def __init__(self, app: Sanic = None, session: SanicSession = None):
        self._app = app
        self._session = session
        self._env = None
        if self._app:
            self.init_app(self._app)

    @property
    def app(self) -> Sanic:
        return self._app  # _context.get()

    def init_app(self, app: Sanic, globals: dict = None):
        self._app = app

        # base dir
        base_dir = app.config.BASE_DIR or '.'

        # init templates dir
        templates_dir = os.path.join(base_dir, "templates")
        logger.debug(f"template init ... templates_dir = {templates_dir}")

        # setup templating environment
        self._env = app.ext.templating.environment

        # self._env.autoescape = False
        # self._env.context_class = SanicTemplateContext
        self._env.trim_blocks = True
        self._env.lstrip_blocks = True
        self._env.loader.searchpath = [templates_dir]
        self._env.globals.update({
            'e': eval,
            'f': format_data
        })
        if globals:
            self._env.globals.update(globals)

        @app.on_request(priority=99)
        async def on_request(request):
            # add session and request
            self._env.globals.update({
                'session': self._session,
                'request': request
            })

        # logger.info(dir(self._env))
        # logger.info(self._env.globals)

    def globals(self, globals: dict):
        if self.app and globals:
            self._env.globals.update(globals)
