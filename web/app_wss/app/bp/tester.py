from sanic import Sanic, Blueprint, Request, app
from sanic.log import logger
from sanic.response import text, json, html, json_dumps
from sanic_ext import render
from sqlalchemy import select

from comm.biz import UserInfo

from web.app.utils import db_session, build_json
from web.app_wss.app.biz.biz_model import SystemConf

bp = Blueprint("tester", url_prefix="tester")


@bp.get("/")
async def index(request):
    # app = Sanic.get_app()
    app = request.app
    return await render("index.html", context={"app_name": f"{app.name}"})


@bp.get("/user")
async def user(request):
    user_info = UserInfo("kylin")
    user_name = await user_info.name("小张-成都")
    logger.warning(f"user_name = {user_name}")
    # return json({"user": f"{user_name}"})
    return build_json({"user": f"{user_name}", "age": 66})


@bp.get("/foo")
async def foo(request):
    user_info = UserInfo("kylin")
    user_name = await user_info.name()
    logger.debug(f"{user_name} enter to foo ...")

    seq = ["a", "b", "c"]
    return await render("foo.html", context={"seq": seq})


@bp.get("/setting/<id:int>")
async def setting(request, id:int):
    async with db_session(request) as session:
        stmt = select(SystemConf).where(SystemConf.id == id)
        result = await session.execute(stmt)
        system_conf = result.scalar()

    return build_json(system_conf.to_dict())