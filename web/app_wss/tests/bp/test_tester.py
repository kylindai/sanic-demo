
import pytest
import unittest

from unittest.mock import Mock, AsyncMock
from tests.async_test_case import AsyncTestCase

from sanic import Sanic, response
from sanic.log import logger

from comm.logger import Logger, LogLevel, LOG_CARE, LOG_ERROR, LOG_IMPORTANT


class TesterTest(AsyncTestCase):

    @pytest.fixture
    def app(self):
        sanic_app = Sanic(__name__)
        logger.info("create app in fixture")
        LOG_CARE("create app in fixture")

        @sanic_app.get("/")
        def basic(request):
            return response.text("foo")

        return sanic_app

    @pytest.mark.run(order=1)
    def test_foo(self):
        logger.info("test_foo")
        assert True

    @pytest.mark.asyncio
    @pytest.mark.run(order=2)
    async def async_test_foo(self):
        logger.info("async_test_foo")
        print("async_test_foo")
        assert True
