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

    def to_dict(self) -> Dict:
        _dict = {
            'id': 0,
            'created': '',
            'modified': ''
        }
        for k in self._sa_class_manager.keys():
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
