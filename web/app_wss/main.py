from sanic import Sanic, Request, response
from sanic.log import logger
from sanic.response.types import JSONResponse

from web.app_wss.app.bp import tester


def create_app() -> Sanic:
    app = Sanic("APP_WSS")

    app.register_listener(main_start, "main_process_start")
    app.register_listener(setup_db, "before_server_start")

    # app.register_middleware(convert_to_json, "response")

    app.static('/static/', 'static')
    app.blueprint(tester.bp)

    # app.config.JSON_AS_ASCII = False

    # @app.on_response
    # async def example(request, response):
    #     print("I execute after the handler.")
    
    
    return app


async def main_start(*_):
    logger.debug("main_start ...")


async def setup_db(*_):
    logger.info("setup_db ...")


async def convert_to_json(request, resp):
    logger.info("convert_to_json ...")
    if isinstance(resp, JSONResponse):
        return response.json(
            resp.raw_body,
            ensure_ascii=False,
            status=getattr(resp, "status", 200)
        )
