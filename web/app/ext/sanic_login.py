
from typing import Type, Coroutine
from functools import wraps

from sanic import Sanic, Request, response
from sanic.log import logger
from sanic.response import json, json_dumps, redirect
from sanic.exceptions import Unauthorized

from .sanic_session import SanicSession


class UserMixin:

    def __init__(self):
        self._logged_in = False

    def get_id(self):
        raise NotImplementedError("get_id() must be implemented")

    def is_active(self):
        raise NotImplementedError("is_active() must be implemented")

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
        self._login_key = None
        self._login_view = None
        self._user_loader: Coroutine[str, None, Type[UserMixin]] = None

        if self._app is not None:
            self.init_app(app)

    @property
    def app(self) -> Sanic:
        return self._app  # _context.get()

    def init_app(self, app):
        logger.debug("login_manager init ...")
        if app.config.LOGIN_CONFIG:
            self._app = app
            self._login_key = app.config.LOGIN_CONFIG.get('LOGIN_KEY')
            self._login_view = app.config.LOGIN_CONFIG.get('LOGIN_VIEW')

    def user_loader(self, func: Coroutine[str, None, Type[UserMixin]]):
        @wraps(func)
        async def deccorated_func(user_id) -> Type[UserMixin]:
            return await func(user_id)
        self._user_loader = deccorated_func
        return deccorated_func

    async def login_user(self, user: UserMixin) -> bool:
        if user:
            user.logged_in = True
            self._session.set(self._login_key, user.get_id())
            return True
        return False

    async def logout_user(self) -> bool:
        user_id = self._session.pop(self._login_key)
        if user_id:
            user = await self._user_loader(user_id)
            if user:
                user.logged_in = False
                return True
        return False

    def login_required(self, func):
        @wraps(func)
        async def decorated_view(request, *args, **kwargs):
            if not await self._user_logged_in(request):
                return redirect(request.app.url_for(self._login_view,
                                                    next=request.path))
            return await func(request, *args, **kwargs)
        return decorated_view

    async def _user_logged_in(self, request):
        user_id = self._session.get(self._login_key, request=request)
        if user_id:
            user = await self._user_loader(user_id)
            if user and user.is_active():
                user.logged_in = True
                return True
