
import time
import uuid
import hashlib

from typing import Optional, Callable, Any
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from functools import wraps

from sanic import Sanic, Request, response, redirect
from sanic.log import logger
from sanic.exceptions import Unauthorized

# from .sanic_session import SanicSession

class UserMixin:

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError(
                "No `id` attribute - override `get_id`") from None


class LoginManager:

    def __init__(self, app=None):
        self.app = app
        self.user_loader = None
        self.request_loader = None
        self.login_view = None
        self.needs_refresh_message = "Session expired, please re-login"
        self.needs_refresh_view = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        
        # 添加上下文处理器
        @app.middleware('request')
        async def load_logged_in_user(request):
            request.ctx.user = self._load_user(request)
        
        # 添加模板全局变量
        if hasattr(app, 'extensions') and 'jinja2' in app.extensions:
            app.extensions.jinja2.env.globals.update(
                current_user=self._get_user
            )
    
    def user_loader(self, callback):
        self.user_loader = callback
        return callback
    
    def request_loader(self, callback):
        self.request_loader = callback
        return callback
    
    def _load_user(self, request):
        if self.request_loader is not None:
            user = self.request_loader(request)
            if user is not None:
                return user
        
        user_id = request.ctx.session.get('user_id')
        if user_id is not None and self.user_loader is not None:
            return self.user_loader(user_id)
        return None
    
    def _get_user(self, request):
        return getattr(request.ctx, 'user', None)
    
    def login_user(self, request, user, remember=False, duration=None):
        request.ctx.session['user_id'] = getattr(user, 'id', user)
        request.ctx.session['_fresh'] = True
        request.ctx.session['_remember'] = remember
        
        if remember:
            request.ctx.session.permanent = True
            if duration is not None:
                request.ctx.session['_remember_seconds'] = duration
    
    def logout_user(self, request):
        user_id = request.ctx.session.pop('user_id', None)
        request.ctx.session.pop('_fresh', None)
        request.ctx.session.pop('_remember', None)
        request.ctx.session.pop('_remember_seconds', None)
        request.ctx.session.pop('_id', None)
        return user_id
    
    def login_required(self, func):
        @wraps(func)
        async def decorated_view(request, *args, **kwargs):
            if not await self._user_is_authenticated(request):
                if self.login_view:
                    return redirect(self.login_view)
                return json({'error': 'Unauthorized'}, status=401)
            return await func(request, *args, **kwargs)
        return decorated_view
    
    async def _user_is_authenticated(self, request):
        user = self._get_user(request)
        return user is not None
    
    def fresh_login_required(self, func):
        @wraps(func)
        async def decorated_view(request, *args, **kwargs):
            if not await self._user_is_authenticated(request):
                if self.login_view:
                    return redirect(self.login_view)
                return json({'error': 'Unauthorized'}, status=401)
            
            if not await self._is_fresh(request):
                if self.needs_refresh_view:
                    return redirect(self.needs_refresh_view)
                return json({'error': self.needs_refresh_message}, status=401)
            
            return await func(request, *args, **kwargs)
        return decorated_view
    
    async def _is_fresh(self, request):
        return request.ctx.session.get('_fresh', False)

async def login_user(
    request: Request,
    user: UserMixin,
    remember: bool = False,
    duration: int = 30*24*3600  # 默认30天
):
    """用户登录"""
    # 验证用户状态
    if not user.is_active():
        raise UserDisabledError("User account is disabled")

    # 更新会话
    await LoginManager._update_session(request, user)

    # 记住我功能
    if remember:
        token = await _generate_remember_token(user)
        request.ctx.session["remember_token"] = token
        request.ctx.session["remember_duration"] = duration


async def logout_user(request: Request):
    """用户登出"""
    request.ctx.session.clear()
    # 应同时清除服务器端记住令牌


async def _generate_remember_token(user: UserMixin) -> str:
    """生成记住我令牌（需自定义实现）"""
    raw_token = f"{user.get_id()}:{uuid.uuid4()}:{time.time()}"
    return hashlib.sha256(raw_token.encode()).hexdigest()

# ---------- 装饰器 ----------


def login_required(func):
    """登录保护装饰器"""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if not getattr(request.ctx, "user", None) or not request.ctx.user.is_authenticated():
            return await handle_unauthorized(request)
        return await func(request, *args, **kwargs)
    return wrapper


def fresh_login_required(func):
    """需要新鲜登录的装饰器"""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        user = getattr(request.ctx, "user", None)
        if not user or not user.is_authenticated() or not request.ctx.session.get("_fresh"):
            return await handle_unauthorized(request, fresh=True)
        return await func(request, *args, **kwargs)
    return wrapper

# ---------- 默认处理器 ----------


async def handle_unauthorized(request: Request, fresh=False):
    """默认未授权处理"""
    manager = request.app.ctx.login_manager
    if manager._unauthorized_handler:
        return await manager._unauthorized_handler(request)
    return response.json({"error": "Unauthorized"}, status=401)

# -------------------------------
# 示例用法
# -------------------------------
app = Sanic("SecureApp")

# 配置Session（示例使用sanic-session）
session = Session()
session.init_app(app)

# 初始化登录管理器
login_manager = LoginManager(app)

# 用户模型


class User(UserMixin):
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.active = True

    def get_id(self) -> str:
        return self.user_id

    def is_active(self) -> bool:
        return self.active

# 用户加载器


@login_manager.user_loader
async def load_user(user_id: str) -> Optional[User]:
    # 这里应查询数据库
    return User(user_id) if user_id == "admin" else None

# 登录路由


@app.post("/login")
async def login(request: Request):
    data = request.json
    # 实际应验证用户名密码
    user = await load_user(data.get("username"))
    if not user or not user.is_active():
        raise InvalidCredentialsError("Invalid credentials")

    await login_user(request, user)
    return response.json({"status": "Logged in"})

# 受保护路由


@app.get("/profile")
@login_required
async def profile(request: Request):
    return response.json({"user": request.ctx.user.get_id()})

# 敏感操作路由（需要新鲜登录）


@app.post("/change-password")
@fresh_login_required
async def change_password(request: Request):
    # 实现密码修改逻辑
    return response.json({"status": "Password changed"})

# 错误处理


@app.exception(InvalidCredentialsError)
async def handle_auth_errors(request, exception):
    return response.json({"error": str(exception)}, status=401)

if __name__ == "__main__":
    app.run(debug=True)
