
from .sanic_session import SanicSession
from .sanic_sqlalchemy import SQLAlchemy
from .sanic_apscheduler import APScheduler

session = SanicSession()
db = SQLAlchemy()
scheduler = APScheduler()
