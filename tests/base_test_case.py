import pytest
import unittest

from sanic.log import logger


class BaseTestCase(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        logger.debug(f"\nTestCase: {cls.__name__} <<<")

    @classmethod
    def teardown_class(cls):
        logger.debug(f"TestCase: {cls.__name__} >>>")

    def setup_method(self, method):
        logger.info(f"before method: {method.__name__}")

    def teardown_method(self, method):
        logger.info(f"after method: {method.__name__}")
