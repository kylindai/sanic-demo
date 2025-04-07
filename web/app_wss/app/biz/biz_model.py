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
