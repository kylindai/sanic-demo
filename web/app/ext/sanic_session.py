
import sanic_cookiesession as cookiesession

from typing import Dict, List

from sanic import Sanic
from sanic.log import logger
from sanic.request import Request
from sanic.response import file


class AttrDict(dict):
    def __getattr__(self, name):
        return self.get(name, None)

class SanicSession:

    def __init__(self, app: Sanic = None):
        self._app = app
        self._ctx = None

        if self._app:
            self.init_app(self._app)

    def __getattr__(self, name):
        if name == 'app':
            return self.app
        elif name == 'ctx':
            return self._ctx
        else:
            return self._ctx.get(name, None)

    @property
    def app(self) -> Sanic:
        return self._app  # _context.get()

    @property
    def ctx(self) -> AttrDict:
        curr_request = Request.get_current()
        if self._app and curr_request:
            self._ctx = getattr(curr_request.ctx, self._session_name)
            return AttrDict(self._ctx or {})
        return AttrDict({})

    def init_app(self, app: Sanic):
        logger.debug("session init ...")
        session_config = app.config.SESSION_CONFIG
        if session_config:
            app.config.update(session_config)
            cookiesession.setup(app)
            self._app = app
            self._session_name = session_config.get('SESSION_NAME')
            # logger.debug(f'session_name = {self._session_name}')

    def get(self, key: str, default_value=None, request: Request = None):
        curr_request = request or Request.get_current()
        if self._app and curr_request:
            self._ctx = getattr(curr_request.ctx, self._session_name)
            return self._ctx.get(key, default_value)

    def set(self, key: str, value, request: Request = None):
        curr_request = request or Request.get_current()
        if self._app and curr_request:
            self._ctx = getattr(curr_request.ctx, self._session_name)
            self._ctx.update({key: value})

    def pop(self, key: str, request: Request = None):
        curr_request = request or Request.get_current()
        if self._app and curr_request:
            self._ctx = getattr(curr_request.ctx, self._session_name)
            if key in self._ctx:
                return self._ctx.pop(key)

    def clear(self, request: Request = None):
        curr_request = request or Request.get_current()
        if self._app and curr_request:
            self._ctx = getattr(curr_request.ctx, self._session_name)
            self._ctx.clear()
