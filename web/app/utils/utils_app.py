import os
import sys
import json
import time

from sanic import Sanic
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
    app.config.update({
        "TEMPLATING_PATH_TO_TEMPLATES": templates_dir,
        "TEMPLATING_ENABLE_ASYNC": True
    })
    app.ext.templating.environment.globals.update(e=eval,
                                                  f=format_data)

    # logger.info("----------")
    # logger.info(dir(app.ext.templating))  # .update()
    # logger.info(app.ext.templating.config)
    logger.info(app.ext.templating.environment.globals)


def build_json(result: dict) -> JSONResponse:
    if result:
        return json(result, indent=4, sort_keys=False, ensure_ascii=False)
    else:
        return json({})
