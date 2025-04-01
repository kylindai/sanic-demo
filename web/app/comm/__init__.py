
from .sanic_sqlalchemy import SQLAlchemy
from .sanic_apscheduler import APScheduler

db = SQLAlchemy()
scheduler = APScheduler()
