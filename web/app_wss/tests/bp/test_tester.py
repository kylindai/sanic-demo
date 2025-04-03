
import pytest
import unittest

from unittest.mock import Mock, AsyncMock

from tests.async_test_case import AsyncTestCase


class TesterTest(AsyncTestCase):

    @pytest.mark.asyncio
    @pytest.mark.run(order=1)
    async def test_foo(self):
        assert True
