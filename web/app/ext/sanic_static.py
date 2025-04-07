import os
import sys
import time

from typing import Dict, List

from sanic import Sanic
from sanic.log import logger
from sanic.request import Request
from sanic.response import file


class SanicStatic:

    def __init__(self, app: Sanic = None):
        self._app = app
        if self._app:
            self.init_app(self._app)

    @property
    def app(self) -> Sanic:
        return self._app  # _context.get()

    def init_app(self, app: Sanic):
        self._app = app

        # base dir
        base_dir = app.config.BASE_DIR or '.'

        # init static dir
        static_dir = os.path.join(base_dir, "static")
        logger.debug(f"static init ... static_dir = {static_dir}")
        app.static('static', static_dir)

        @app.on_request(priority=99)
        async def on_request(request):
            # skip request handlers
            if request.path.startswith("/static/"):
                return await file(f"{base_dir}/{request.path}")
            # else:
                # logger.debug(f"static on_request: {request.path}")

        @app.on_response(priority=-1)
        async def on_response(request, response):
            # skip response handlers
            if request.path.startswith("/static/"):
                return response
            # else:
                # logger.debug(f"static on_response: {request.path}")
