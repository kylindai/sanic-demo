from sanic import Sanic, Blueprint, Request, app
from sanic.log import logger
from sanic.response import text, json, html, json_dumps
from sanic_ext import render

from comm.biz import UserInfo
from web.app.utils import build_json

bp = Blueprint("tester")


@bp.get("/tester")
async def index(request):
    user_info = UserInfo("kylin")
    user_name = await user_info.name("小张-成都")
    logger.warning(f"user_name = {user_name}")
    # return json({"user": f"{user_name}"})
    return build_json({"user": f"{user_name}", "age": 66})


@bp.get("/tester/foo")
async def foo(request):
    user_info = UserInfo("kylin")
    user_name = await user_info.name()
    logger.debug(f"{user_name} enter to foo ...")

    return await render("foo.html")
