
# from sanic_session import Session
import sanic_cookiesession as session

from .sanic_sqlalchemy import SQLAlchemy
from .sanic_apscheduler import APScheduler

# session = Session()
db = SQLAlchemy()
scheduler = APScheduler()
