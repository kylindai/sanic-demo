
import time
import uuid
import hashlib

from typing import Optional, Callable, Any
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from functools import wraps

from sanic import Sanic, Request, response
from sanic.log import logger
from sanic.response import json, json_dumps, redirect
from sanic.exceptions import Unauthorized

from .sanic_session import SanicSession


class UserMixin:

    def __init__(self):
        self._user_id = None
        self._logged_in = False

    @property
    def user_id(self):
        return self._user_id

    @property
    def logged_in(self):
        return self._logged_in

    @logged_in.setter
    def logged_in(self, value: bool):
        self._logged_in = value


class LoginManager:

    def __init__(self, app: Sanic = None, session: SanicSession = None):
        self._app = app
        self._session = session
        self._login_view = None
        self._user_loader = None

        if self._app is not None:
            self.init_app(app)

    @property
    def app(self) -> Sanic:
        return self._app  # _context.get()

    def init_app(self, app):
        if app.config.LOGIN_CONFIG:
            self._app = app
            self._login_view = app.config.LOGIN_CONFIG.get('LOGIN_VIEW')

    def user_loader(self, async_func):
        self._user_loader = async_func
        return async_func

    async def _load_user(self):
        user_id = self._session.get('LOGIN_USER_ID')
        if user_id and self._user_loader:
            return await self._user_loader(user_id)

    async def _user_logged_in(self):
        user_id = self._session.get('LOGIN_USER_ID')
        if user_id:
            user = await self._user_loader(user_id)
            if user:
                return user.logged_in

    async def login_user(self, user_id: str) -> bool:
        if user_id:
            user = await self._user_loader(user_id)
            if user:
                user.logged_in = True
                self._session.set('LOGIN_USER_ID', user_id)
                return True
        return False

    async def logout_user(self) -> bool:
        user_id = self._session.pop('LOGIN_USER_ID')
        if user_id:
            user = await self._user_loader(user_id)
            if user:
                user.logged_in = False
                return True
        return False

    def login_required(self, func):
        @wraps(func)
        async def decorated_view(request, *args, **kwargs):
            if not await self._user_logged_in():
                return redirect(request.app.url_for(self._login_view,
                                                    next=request.path))
            return await func(request, *args, **kwargs)
        return decorated_view
