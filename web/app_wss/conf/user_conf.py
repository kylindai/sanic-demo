
from werkzeug.security import generate_password_hash

Config = [
    {
        'id': '1',
        'name': 'miaowa',
        'active': False,
        'password': generate_password_hash('123456')
    },
    {
        'id': '2',
        'name': 'admin',
        'active': True,
        'password': generate_password_hash('123456')
    },
]