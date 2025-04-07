import ast
import math
import time
import json
import numpy as np
import pandas as pd

from datetime import datetime

from comm import Logger, LOG_IMPORTANT
from comm.utils import get_datetime


def eval(obj_string: str):
    if not obj_string:
        return ''
    try:
        return ast.literal_eval(obj_string)
    except Exception as e:
        LOG_IMPORTANT(e)
        return ''


def format_data(data: object, fmt: str = None, none_value: str = '-'):
    if not data:
        if isinstance(data, (int, float)):
            if fmt is not None:
                return fmt.format(data)
            else:
                return data
        else:
            return f"<span class='text-muted'>{none_value}</span>"
    else:
        if isinstance(data, str):
            if fmt is None:
                return data
            elif fmt == '%a' or fmt == '%A':
                return get_datetime(data, '%Y%m%d').strftime(fmt)
            else:
                return data
        elif isinstance(data, (int, float)):
            if fmt is not None:
                if np.isnan(data):
                    return f"<span class='text-muted'>{none_value}</span>"
                else:
                    return fmt.format(data)
            else:
                return data
        elif isinstance(data, (datetime)):
            if fmt == 'ts':
                return int(data.timestamp())
            return data
        else:
            return data
