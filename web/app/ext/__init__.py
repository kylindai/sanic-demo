
from .sanic_static import SanicStatic
from .sanic_sqlalchemy import SQLAlchemy
from .sanic_session import SanicSession
from .sanic_template import SanicTemplate
from .sanic_login import LoginManager
from .sanic_apscheduler import APScheduler

static = SanicStatic()
db = SQLAlchemy()
session = SanicSession()
template = SanicTemplate(session=session)
login_manager = LoginManager(session=session)
scheduler = APScheduler()
