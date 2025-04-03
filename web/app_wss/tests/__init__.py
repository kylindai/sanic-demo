import pytest

from sanic import Sanic, request, response
from sanic.log import logger


@pytest.fixture(scope="class")
def test_app():
    sanic_app = Sanic('APP_WSS')
    logger.debug("create app in fixture")

    @sanic_app.get("/")
    def index(request):
        return response.text("foo")

    return sanic_app
