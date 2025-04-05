import os
import sys
import json
import time
import asyncio
import datetime

from datetime import datetime
from sanic import Sanic, Blueprint, Request, response
from sanic.log import logger
from sanic.response import text, json, html, json_dumps, redirect
from sanic_ext import render
from sqlalchemy import select
from werkzeug.security import generate_password_hash

from comm.biz import UserInfo
from web.app.comm.sanic_login import UserMixin

from web.app.comm import db, scheduler, session, login_manager
from web.app.utils import build_json
from web.app_wss.conf import user_config
from web.app_wss.app.biz.biz_model import SystemConf

bp = Blueprint("tester", url_prefix="tester")


async def async_task_4(task_id, job_id):
    try:
        logger.debug(f"async_task_4 ... {task_id}, {job_id}")
        await asyncio.sleep(1)
    except asyncio.CancelledError as e:
        logger.warning(e)


class User(UserMixin):

    def __init__(self, user: dict):
        self._user_id = user.get('user_id')
        self._user_name = user.get('user_name')
        self._user_admin = user.get('user_admin')
        self._user_password = user.get('user_password')

    @property
    def user_id(self):
        return self._user_id
    
    @staticmethod
    def get_user_by_name(user_name: str):
        for user in user_config:
            if user.get('user_name') == user_name:
                return User(user)

    def check_password(self, password: str) -> bool:
        return self._user_password == generate_password_hash(password)


@login_manager.user_loader
async def load_user(user_id):
    logger.debug(f"load_user ... {user_id}")
    for user in user_config:
        if user.get('user_id') == user_id:
            return User(user)


@bp.get("/")
async def index(request):
    session.pop('user_name')
    user_name = session.get('user_name')
    if not user_name:
        user_name = 'miaowa'
        session.set('user_name', user_name)
    user_address = session.get('user_address')
    return await render("index.html", context={
        "app_name": f"{request.app.name}",
        "user_name": user_name,
        "user_address": user_address
    })


@bp.get("/login")
async def login(request):
    next = request.args.get('next')
    return await render("login.html",
                        context={
                            "username": session.get('user_name')
                        })


@bp.post("/user_login")
async def user_login(request):
    username = request.form.get('username') or ''
    password = request.form.get('password')

    next = request.args.get('next')
    target = request.app.url_for('tester.login', next=next)

    user = User.get_user_by_name(username)
    if user and user.check_password(password):
        if login_manager.login_user(user.user_id):
            if next:
                target = request.app.url_for(next)
            else:
                target = request.app.url_for('tester.index')
            return redirect(target)

    return await login(request)


@bp.get("/user")
@login_manager.login_required
async def user(request):
    user_info = UserInfo("kylin")
    user_name = await user_info.name("小张-成都")
    logger.warning(f"user_name = {user_name}")
    # return json({"user": f"{user_name}"})
    return build_json({"user": f"{user_name}", "age": 66})


@bp.get("/foo")
async def foo(request):
    user_info = UserInfo("kylin")
    user_name = session.get('user_name')
    # logger.debug(f"{user_name} enter to foo ...")

    seq = ["a", "b", "c"]
    return await render("foo.html", context={
        "seq": seq, "user_name": user_name})


@bp.get("/setting/<id:int>")
async def setting(request, id: int):
    async with db.session() as session:
        stmt = select(SystemConf).where(SystemConf.id == id)
        result = await session.execute(stmt)
        system_conf = result.scalar()

    return build_json(system_conf.to_dict())


@bp.get("/system/<id:int>")
async def setting(request, id: int):
    async with db.session() as session:
        stmt = select(SystemConf).where(SystemConf.id == id)
        result = await session.execute(stmt)
        system_conf = result.scalar()

    return build_json(system_conf.to_dict())


@bp.post("/task")
async def task(request):
    client_id = request.form.get('client', 0)
    logger.debug(f'client_id = {client_id}')
    job = scheduler.add_job("async_task_4", async_task_4, 'interval',
                            args=(1, client_id), seconds=2)
    return build_json({'job': str(job)})


@bp.get("/sse")
@login_manager.login_required
async def sse(request):
    return await render("sse.html", context={"sse_host": "localhost:8001"})


@bp.get("/stream")
async def stream(request):
    async def event_stream(response, id):
        try:
            while True:
                ts = int(time.time())
                data = {'id': id, 'ts': ts}
                message = f'id: {id}\nevent: greeting\ndata: {json_dumps(data)}\n\n'
                await response.send(message)
                await asyncio.sleep(1)
                id = id + 1
                logger.debug(f"event_stream send message ... {message}")
                if id > 10:
                    break
            await response.eof()
        except asyncio.CancelledError:
            logger.warning('client disconnect')
            await response.eof()

    response = await request.respond(content_type='text/event-stream',
                                     headers={
                                         'Cache-Control': 'no-cache',
                                         'Connection': 'keep-alive'
                                     })
    await event_stream(response, 1)


@bp.get("/wss")
async def sse(request):
    return await render("wss.html", context={"wss_host": "localhost:8001"})
