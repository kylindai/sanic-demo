
import pytest
import unittest

from unittest.mock import Mock, AsyncMock

from sanic import Sanic, response
from sanic.log import logger
from sanic_testing.reusable import ReusableClient

from web.app_wss.tests import test_app


class TesterTest:

    @pytest.mark.run(order=1)
    def test_foo(self, test_app):
        logger.info("test_foo")
        client = ReusableClient(test_app)
        with client:
            request, response = client.get("/")
            assert request.method.lower() == "get"
            assert response.body == b"foo"
            assert response.status == 200

    @pytest.mark.asyncio
    @pytest.mark.run(order=2)
    async def test_foo_async(self, test_app):
        logger.info("test_foo_async")
        request, response = await test_app.asgi_client.get("/")
        assert request.method.lower() == "get"
        assert response.body == b"foo"
        assert response.status == 200
