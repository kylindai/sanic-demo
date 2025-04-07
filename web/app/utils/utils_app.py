import os
import sys
import time

from sanic import Sanic, Request
from sanic.log import logger
from sanic.response import json
from sanic.response.types import JSONResponse
from sanic_ext import render as sanic_ext_render

def init_app(app: Sanic):
    # base dir
    pass


def url_for(view_name: str, **kwargs) -> str:
    return Sanic.url_for(view_name, **kwargs)


def render(template: str, **kwargs):
    return sanic_ext_render(template, context={str(key): value for key, value in kwargs.items()})


def build_json(result: dict) -> JSONResponse:
    if result:
        return json(result, indent=4, sort_keys=False, ensure_ascii=False)
    else:
        return json({})
