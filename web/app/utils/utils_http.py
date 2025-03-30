import os
import sys
import json
import time

from sanic import Sanic
from sanic.log import logger
from sanic.response import json
from sanic.response.types import JSONResponse


from sqlalchemy.ext.asyncio import AsyncSession


def init_app(app: Sanic):
    # base dir
    base_dir = app.config.BASE_DIR or '.'
    # init static dir
    static_dir = os.path.join(base_dir, "static")
    app.static('static', static_dir)
    # init templates dir
    templates_dir = os.path.join(base_dir, "templates")
    app.config.TEMPLATING_PATH_TO_TEMPLATES = templates_dir


def db_session(request) -> AsyncSession:
    if request.app.ctx.db_session:
        return request.app.ctx.db_session()


def build_json(resp: dict) -> JSONResponse:
    if resp:
        return json(resp, indent=4, sort_keys=False, ensure_ascii=False)
    else:
        return json({})
