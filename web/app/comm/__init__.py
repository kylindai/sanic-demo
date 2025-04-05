
from .sanic_session import SanicSession
from .sanic_sqlalchemy import SQLAlchemy
from .sanic_apscheduler import APScheduler
from .sanic_login import LoginManager

session = SanicSession()
db = SQLAlchemy()
scheduler = APScheduler()
login_manager = LoginManager(session=session)
