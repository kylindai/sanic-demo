
from werkzeug.security import generate_password_hash

Config = [
    {
        'id': '1',
        'name': 'miaowa',
        'admin': False,
        'password': generate_password_hash('123456')
    },
    {
        'id': '2',
        'name': 'admin',
        'admin': True,
        'password': generate_password_hash('123456')
    },
]