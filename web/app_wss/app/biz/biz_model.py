import json
import time
import datetime

from typing import List, Dict, Tuple
from dataclasses import dataclass

from web.app.ext import db


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP)
    modified = db.Column(db.TIMESTAMP)

    def __repr__(self) -> str:
        columns = self.__columns()
        fields = ['{0}={1}'.format(c, getattr(self, c))
                  for c in columns]
        return "{}({})".format(self.__class__.__tablename__, ",".join(fields))

    def __columns(self) -> List[str]:
        c = ['id', 'created', 'modified']
        keys = self._sa_class_manager.keys()
        columns = []
        columns.extend(c)
        columns.extend([k for k in keys if k not in c])
        return columns

    def to_dict(self) -> Dict:
        _dict = {
            'id': 0,
            'created': '',
            'modified': ''
        }
        keys = self._sa_class_manager.keys()
        for k in keys:
            v = getattr(self, k)
            if isinstance(v, datetime.datetime):
                v = v.strftime("%Y-%m-%d %H:%M:%S.%f")
            _dict[k] = v
        return _dict


class SystemConf(BaseModel):
    __tablename__ = 'S_SYSTEM_CONF'

    type = db.Column(db.String)
    name = db.Column(db.String)
    start_time = db.Column(db.String)
    end_time = db.Column(db.String)
    conf_key = db.Column(db.String)
    conf_value = db.Column(db.String)
    status = db.Column(db.String)


class Symbol(BaseModel):
    __tablename__ = 'S_SYMBOL'

    id = db.Column(db.Integer, primary_key=True)
    modified = db.Column(db.TIMESTAMP)
    type = db.Column(db.String)
    code = db.Column(db.String)
    name = db.Column(db.String)
    term = db.Column(db.String)
    market = db.Column(db.String)
    symbol = db.Column(db.String)
    exchange = db.Column(db.String)
    instrument = db.Column(db.String)
    open_date = db.Column(db.String)
    expire_date = db.Column(db.String)
    is_trading = db.Column(db.Integer)


class SymbolExt(BaseModel):
    __tablename__ = 'S_SYMBOL_EXT'

    id = db.Column(db.Integer, primary_key=True)
    modified = db.Column(db.TIMESTAMP)
    broker_id = db.Column(db.String)
    user_id = db.Column(db.String)
    symbol = db.Column(db.String)
    price_tick = db.Column(db.Integer)
    tick_price = db.Column(db.Float)
    commission_open = db.Column(db.Float)
    commission_close = db.Column(db.Float)
    max_limit_order_volume = db.Column(db.Integer)
    min_limit_order_volume = db.Column(db.Integer)
    max_market_order_volume = db.Column(db.Integer)
    min_market_order_volume = db.Column(db.Integer)
    long_margin_ratio = db.Column(db.Float)
    short_margin_ratio = db.Column(db.Float)
    volume_multiple = db.Column(db.Float)
    underlying_multiple = db.Column(db.Float)
