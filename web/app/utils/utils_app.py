import os
import sys
import json
import time

from sanic import Sanic, Request
from sanic.log import logger
from sanic.response import json
from sanic.response.types import JSONResponse

from .utils_html import eval, format_data


def init_app(app: Sanic):
    # Extend(app)

    # base dir
    base_dir = app.config.BASE_DIR or '.'

    # init static dir
    static_dir = os.path.join(base_dir, "static")
    app.static('static', static_dir)

    # init templates dir
    templates_dir = os.path.join(base_dir, "templates")
    # setup templating environment
    # app.ext.templating.environment.autoescape = False
    app.ext.templating.environment.trim_blocks = True
    app.ext.templating.environment.lstrip_blocks = True
    app.ext.templating.environment.loader.searchpath = [templates_dir]
    app.ext.templating.environment.globals.update({
        'e': eval,
        'f': format_data
    })

    # logger.info(app.ext.templating.config)
    # logger.info(dir(app.ext.templating.environment))
    # logger.info(app.ext.templating.environment.globals)


def url_for(endpoint: str, **kwargs) -> str:
    return Request.get_current().app.url_for(endpoint, **kwargs)


def build_json(result: dict) -> JSONResponse:
    if result:
        return json(result, indent=4, sort_keys=False, ensure_ascii=False)
    else:
        return json({})
