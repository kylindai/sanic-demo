
import os
import sys
import time
import json
import datetime
import sqlalchemy

from typing import Dict, List, Tuple
from collections.abc import Iterable

from sanic import Sanic
from sanic.log import logger

from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Select, Insert, Update, Delete, select, insert, update, delete, func


class Pagination():
    """
    - page # page no
    - size # page size
    - total # row count
    - pages # page count
    - items # list of data
    """

    def __init__(self, page: int, size: int, total: int, pages: int, items: List):
        self.page = page
        self.size = size
        self.total = total
        self.pages = pages
        self.items = items

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def prev_page(self) -> int:
        return 1 if not self.has_prev else self.page - 1

    @property
    def next_page(self) -> int:
        return self.pages if not self.has_next else self.page + 1

    def __repr__(self) -> str:
        return str({
            'page': self.page,
            'size': self.size,
            'total': self.total,
            'pages': self.pages,
            'items': self.items,
            'has_prev': self.has_prev,
            'has_next': self.has_next,
            'prev_page': self.prev_page,
            'next_page': self.next_page
        })


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
        logger.debug("db init ...")
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

    async def query_first(self, stmt: Select):
        """
        - return the first row
          - tuple(model_1, model_2) when select(model_1, model_2)
          - model_1 when select(model_1)
          - None when without result
        """
        async with self._session_maker() as session:
            result = await session.execute(stmt.limit(1))

        if result:
            rows = result.all()
            if len(rows) > 0:
                row = rows[0]
                return row if len(row) > 1 else row[0]
            # for row in result.all():
            #     if len(row) > 1:
            #         # multi models
            #         return row
            #     else:
            #         # single model
            #         return row[0]

    async def query_all(self, stmt: Select) -> List:
        """
        - return the all rows
          - [tuple(model_1, model_2)] when select(model_1, model_2)
          - [model_1] when select(model_1)
          - [] when without result
        """
        async with self._session_maker() as session:
            result = await session.execute(stmt)

        if result:
            return [row if len(row) > 1 else row[0]
                    for row in result.all()]
        return []

    async def query_paginate(self, stmt: Select, page: int = 1, size: int = 20) -> Pagination:
        """
        - param stmt # select
        - param page # page_no from 1
        - param size # size
        - return Paginate
        """
        async with self._session_maker() as session:
            # count
            total_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await session.execute(total_stmt)
            total = total_result.scalar_one()
            pages = (total + size - 1) // size
            items_result, items = None, []
            if total > 0:
                # paginate
                offset = (page - 1) * size
                items_stmt = stmt.limit(size).offset(offset)
                items_result = await session.execute(items_stmt)

        if items_result:
            """
            - items:
            - [tuple(model_1, model_2)] when select(model_1, model_2)
            - [model_1] when select(model_1)
            - [] when without result
            """
            items = [row if len(row) > 1 else row[0]
                     for row in items_result.all()]

        return Pagination(page, size, total, pages, items)

    async def execute(self, stmt: Insert | Update | Delete) -> int:
        async with self._session_maker() as session:
            result = await session.execute(stmt)
            await session.commit()

        if isinstance(stmt, Insert):
            return result.inserted_primary_key[0]
        else:
            return result.rowcount

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
            echo = db_config.get('echo', False)
            engine = create_async_engine(db_url,
                                         pool_size=10,
                                         max_overflow=5,
                                         pool_recycle=3600,
                                         pool_timeout=30,
                                         pool_pre_ping=True,
                                         echo=echo)
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
