
import sanic_cookiesession as cookiesession

from typing import Dict, List

from sanic import Sanic
from sanic.log import logger
from sanic.request import Request


class SanicSession:

    def __init__(self, app: Sanic = None):
        self._app = app
        if self._app:
            self.init_app(self._app)

    @property
    def app(self) -> Sanic:
        return self._app  # _context.get()

    def init_app(self, app: Sanic):
        self._app = app
        cookiesession.setup(app)

    def get(self, key: str, default_value=None):
        request = Request.get_current()
        if self._app and request:
            value = request.ctx.session.get(key)
            if not value:
                return default_value
            return value

    def set(self, key: str, value):
        request = Request.get_current()
        if self._app and request:
            request.ctx.session.setdefault(key, value)

    def pop(self, key):
        request = Request.get_current()
        if self._app and request:
            return request.ctx.session.pop(key)

    def clear(self):
        request = Request.get_current()
        if self._app and request:
            request.ctx.session.clear()
