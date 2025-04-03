
from sanic_session import Session

from .sanic_sqlalchemy import SQLAlchemy
from .sanic_apscheduler import APScheduler

session = Session()
db = SQLAlchemy()
scheduler = APScheduler()
