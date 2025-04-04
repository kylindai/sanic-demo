
import os
import sys
import time
import json
import datetime
import sqlalchemy

from typing import Dict, List

from sanic import Sanic
from sanic.log import logger

from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship


class SQLAlchemy:

    Column = sqlalchemy.Column
    Integer = sqlalchemy.Integer
    Float = sqlalchemy.Float
    String = sqlalchemy.String

    INT = sqlalchemy.INT
    BIGINT = sqlalchemy.BIGINT
    TIME = sqlalchemy.TIME
    TIMESTAMP = sqlalchemy.TIMESTAMP
    VARCHAR = sqlalchemy.VARCHAR

    Model = declarative_base()

    def __init__(self):
        self._app = None
        self._connected = False

    @property
    def app(self) -> Sanic:
        return self._app  # _context.get()

    def init_app(self, app: Sanic):
        # logger.debug(app.config.DB_CONFIG)
        db_engine = self._create_engine(app.config.DB_CONFIG)
        if db_engine:
            self._app = app
            # register listener engine
            app.ctx.db_engine = db_engine
            app.register_listener(self._connect_db, "after_server_start")
            app.register_listener(self._disconnect_db, "before_server_stop")
            # logger.debug("register listener db_engine ok")

    def session(self) -> AsyncSession:
        if self._connected:
            return self._session_maker()

    def _get_db_url(self, db_config) -> str:
        if db_config and 'host' in db_config and 'port' in db_config \
                and 'username' in db_config and 'password' in db_config \
                and 'database' in db_config:
            host = db_config['host']
            port = db_config['port']
            username = db_config['username']
            password = db_config['password']
            database = db_config['database']
            return f"mysql+aiomysql://{username}:{password}@{host}:{port}/{database}"

    def _create_engine(self, db_config: Dict):
        db_url = self._get_db_url(db_config)
        if db_url:
            engine = create_async_engine(db_url,
                                         pool_size=10,
                                         max_overflow=5,
                                         pool_recycle=3600,
                                         pool_timeout=30,
                                         pool_pre_ping=True,
                                         echo=False)
            self._session_maker = async_sessionmaker(engine,
                                                     expire_on_commit=False)
            return engine

    async def _connect_db(self, app, loop):
        if app.ctx.db_engine:
            self._connected = True
            # await app.ctx.db_engine.connect()
            logger.info("db connected")

    async def _disconnect_db(self, app, loop):
        if app.ctx.db_engine:
            await app.ctx.db_engine.dispose()
            self._connected = False
            logger.info("db disconnected")
