
import os
import re
import sys
import time
import shutil
import asyncio
import logging
import functools

from typing import Dict, List, Union
from enum import Enum
from datetime import datetime
from logging import LogRecord

ANSI_WEAKEN = "\033[2m"
ANSI_BLACK = "\033[30m"
ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_BLUE = "\033[34m"
ANSI_PINK = "\033[35m"
ANSI_CYAN = "\033[36m"
ANSI_WHITE = "\033[37m"
ANSI_LIGHT_BLACK = "\033[90m"
ANSI_LIGHT_RED = "\033[91m"
ANSI_LIGHT_GREEN = "\033[92m"
ANSI_LIGHT_YELLOW = "\033[93m"
ANSI_LIGHT_BLUE = "\033[94m"
ANSI_LIGHT_PINK = "\033[95m"
ANSI_LIGHT_CYAN = "\033[96m"
ANSI_LIGHT_WHITE = "\033[97m"
ANSI_REMOVE_COLOR = "\033[0m"


def LOG_PROGRESS(x):
    print(f"\r{ANSI_LIGHT_PINK}{x}{ANSI_REMOVE_COLOR}", end='')


def LOG_IMPORTANT(x):
    print(f"{ANSI_LIGHT_PINK}{x}{ANSI_REMOVE_COLOR}")


def LOG_IGNORE(x):
    print(f"{ANSI_WEAKEN}{x}{ANSI_REMOVE_COLOR}")


def LOG_ERROR(x):
    print(f"{ANSI_RED}{x}{ANSI_REMOVE_COLOR}")


def LOG_CARE(x):
    print(f"{ANSI_LIGHT_CYAN}{x}{ANSI_REMOVE_COLOR}")


def LOG_KV(key, value):
    print(
        f"{ANSI_YELLOW}{key} = [{ANSI_GREEN}{value}{ANSI_YELLOW}]{ANSI_REMOVE_COLOR}")


class LogLevel(Enum):
    IGNORE = ('IGR', 10, ANSI_WEAKEN)
    TRACE = ('TRC', 20, ANSI_BLUE)
    DEBUG = ('DBG', 30, ANSI_GREEN)
    INFO = ('INF', 40, ANSI_WHITE)
    CARE = ('CRE', 50, ANSI_LIGHT_CYAN)
    WARN = ('WRN', 60, ANSI_YELLOW)
    ALERT = ('ALT', 70, ANSI_LIGHT_PINK)
    ERROR = ('ERR', 80, ANSI_RED)
    FATAL = ('FTL', 90, ANSI_RED)


class LogHandler(logging.Handler):

    class Filter(logging.Filter):

        def __init__(self, log_level: LogLevel):
            super().__init__()
            self._log_level = log_level

        def do_filter(self, log_level: LogLevel):
            if log_level.value[1] < LogLevel.DEBUG.value[1]:
                return True
            return log_level.value[1] >= self._log_level.value[1]

        def filter(self, record):
            log_level = getattr(record, 'LogLevel')
            return self.do_filter(log_level)

    def __init__(self, name: str, log_level: LogLevel):
        super().__init__()

        self._name = name
        self._log_level = log_level

        self._filter = LogHandler.Filter(log_level)
        self.addFilter(self._filter)

    def name(self, name: str):
        self._name = name

    def log_level(self):
        return self._log_level

    def get_filter(self):
        return self._filter


class ConsoleLogHandler(LogHandler):

    class Formatter(logging.Formatter):
        def __init__(self, format: str = '%(message)s'):
            super().__init__(format)

        @staticmethod
        def do_format(name: str, log_level: LogLevel, created: float, msg: str) -> str:
            color = log_level.value[2]
            level = log_level.value[0]
            return f"{datetime.fromtimestamp(created)}: {color}[{level}] {name}: {msg}{ANSI_REMOVE_COLOR}"

        def format(self, record: LogRecord):
            name = getattr(record, 'name')
            log_level = getattr(record, 'LogLevel')
            created = getattr(record, 'created')
            msg = getattr(record, 'msg')

            setattr(record, 'log_msg',
                    ConsoleLogHandler.Formatter.do_format(name, log_level, created, msg))

    def __init__(self, name: str, log_level: LogLevel):
        super().__init__(name, log_level)
        self.setFormatter(ConsoleLogHandler.Formatter())

    def emit(self, record: LogRecord):
        self.format(record)
        print(record.log_msg)

    def close(self):
        super().close()


class FileLogHandler(LogHandler):

    _log_file_name = None
    _log_file = None

    class Formatter(logging.Formatter):
        def __init__(self, format: str = '%(message)s'):
            super().__init__(format)

        @staticmethod
        def do_format(name: str, log_level: LogLevel, created: float, msg: str) -> str:
            return f"{datetime.fromtimestamp(created)}: [{log_level.value[0]}] {name}: {msg}\n"

        def format(self, record: LogRecord):
            name = getattr(record, 'name')
            log_level = getattr(record, 'LogLevel')
            created = getattr(record, 'created')
            msg = getattr(record, 'msg')

            setattr(record, 'log_msg',
                    FileLogHandler.Formatter.do_format(name, log_level, created, msg))

    def __init__(self, name: str, log_level: LogLevel, log_file_name: str):
        super().__init__(name, log_level)
        self.setFormatter(FileLogHandler.Formatter())
        self._set_log_file_name(log_file_name)

    def emit(self, record: LogRecord):
        self.format(record)

        if FileLogHandler._log_file is not None:
            try:
                FileLogHandler._log_file.write(record.log_msg)
                FileLogHandler._log_file.flush()
            except Exception as e:
                pass

    def close(self):
        if FileLogHandler._log_file is not None:
            FileLogHandler._log_file.close()
            FileLogHandler._back_log_file()

    @staticmethod
    def _set_log_file_name(file_name: str = None):
        log_path = os.path.abspath("./log")
        if not os.path.exists(log_path):
            os.makedirs(log_path, exist_ok=True)
        if file_name is None:
            file_name = f"{os.path.splitext(sys.argv[0])[0]}.log"
        FileLogHandler._log_file_name = os.path.join(log_path, file_name)
        try:
            FileLogHandler._log_file = open(
                FileLogHandler._log_file_name, "w+")
        except Exception as e:
            print(e)

    @staticmethod
    def _back_log_file():
        if not FileLogHandler._log_file_name:
            return
        file_old = os.path.join(FileLogHandler._log_file_name)
        if not os.path.exists(file_old):
            return
        # log bak path
        log_path = os.path.dirname(FileLogHandler._log_file_name)
        file_name = os.path.basename(FileLogHandler._log_file_name)
        log_bak_path = os.path.join(log_path, "bak")
        if not os.path.exists(log_bak_path):
            os.makedirs(log_bak_path, exist_ok=True)
        # log bak file name
        file_prefix = os.path.splitext(file_name)[0]
        file_date = datetime.now().strftime('%Y%m%d')
        file_seq = 0
        # find file seq
        file_list = os.listdir(log_bak_path)
        if file_list:
            file_pattern = re.compile(f"{file_prefix}-{file_date}-(\\d+).log")
            for file in file_list:
                if file_pattern.search(file):
                    seq = int(file_pattern.search(file).group(1))
                    file_seq = max(file_seq, seq)
        file_bak = os.path.join(
            log_bak_path, f"{file_prefix}-{file_date}-{file_seq+1}.log")
        shutil.move(file_old, file_bak)


class Logger:

    Level = LogLevel

    _root_name = ''
    _log_level = LogLevel.INFO

    def __init__(self,
                 name: Union[str, object],
                 sub_name: str = None,
                 log_level: LogLevel = LogLevel.INFO,
                 log_file_name: str = None,
                 trace: bool = False):
        if isinstance(name, str):
            if not Logger._root_name:
                Logger._root_name = name
            self._name = name
        else:
            self._name = name.__class__.__name__

        # for sub logger
        if sub_name is not None:
            self._name = self._name + '.' + sub_name

        if log_level is not None:
            Logger._log_level = log_level
        self._log_level = Logger._log_level

        self._trace = trace

        self._logger = None

        self._logger = logging.getLogger(self._logger_name())
        # self._logger.propagate = False
        self._logger.setLevel(logging.ERROR)
        # set handler for root logger
        self._setup_handler(log_file_name)

        if self._trace:
            self._start = time.time()
            self._log(LogLevel.TRACE, '<<<')

    def __del__(self):
        if self._trace:
            cost = (time.time() - self._start) * 1000.0
            trace_left = '>>>'
            if cost < 1000:
                trace_left = f'>>> cost: {cost:.3f}ms'
            elif cost < 60000:
                trace_left = f'>>> cost: {(cost/1000.0):.3f}s'
            elif cost < 3600000:
                trace_left = f'>>> cost: {(cost/60000.0):.3f}m'
            else:
                trace_left = f'>>> cost: {(cost/3600000.0):.3f}h'
            self._log(LogLevel.TRACE, trace_left)

    def _logger_name(self):
        if Logger._root_name and Logger._root_name != self._name:
            return f'{Logger._root_name}.{self._name}'
        else:
            return self._name

    def _is_root_logger(self):
        return Logger._root_name == self._name

    def _setup_handler(self, log_file_name):
        if self._is_root_logger():
            # check handler
            has_console_handler, has_file_handler = False, False
            for handler in self._logger.handlers:
                if isinstance(handler, ConsoleLogHandler):
                    has_console_handler = True
                if isinstance(handler, FileLogHandler):
                    has_file_handler = True

            # console log handler
            if not has_console_handler:
                console_log_handler = ConsoleLogHandler(self._name,
                                                        self._log_level)
                self._logger.addHandler(console_log_handler)
            # file log handler
            if log_file_name and not has_file_handler:
                file_log_handler = FileLogHandler(self._name,
                                                  LogLevel.IGNORE,
                                                  log_file_name)
                self._logger.addHandler(file_log_handler)

    def _log(self, log_level: LogLevel, message: str):
        self._logger.error(message, extra={'LogLevel': log_level})

    def name(self):
        return self._name

    def ignore(self, message: str):
        self._log(LogLevel.IGNORE, message)

    def trace(self, message: str):
        self._log(LogLevel.TRACE, message)

    def debug(self, message: str):
        self._log(LogLevel.DEBUG, message)

    def info(self, message: str):
        self._log(LogLevel.INFO, message)

    def care(self, message: str):
        self._log(LogLevel.CARE, message)

    def warn(self, message: str):
        self._log(LogLevel.WARN, message)

    def alert(self, message: str):
        self._log(LogLevel.ALERT, message)

    def error(self, message: str):
        self._log(LogLevel.ERROR, message)

    def fatal(self, message: str):
        self._log(LogLevel.FATAL, message)
