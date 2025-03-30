from sanic.response import json
from sanic.response.types import JSONResponse


def build_json(resp: dict) -> JSONResponse:
    if resp:
        return json(resp, indent=4, sort_keys=False, ensure_ascii=False)
    else:
        return json({})
