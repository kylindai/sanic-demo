
from web.app_wss.app.job.test_job import test_task_1
from web.app_wss.app.job.test_job import async_task_1

Jobs = [
    {
        'id': 'test_task_1',
        'use': False,
        'func': 'web.app_wss.app.job.test_job:test_task_1',
        'args': (1, 2),
        'trigger': {
            'type': 'cron',
            'day': '*',
            'hour': '*',
            'minute': '*',
            'second': '*/15'
        }
    },
    {
        'id': 'async_task_1',
        'use': False,
        'func': async_task_1,
        'args': (1, 3),
        'trigger': {
            'type': 'cron',
            'second': '*/13'
        }
    },
]

Config = {
    'JOBS': Jobs,
    'SCHEDULER_JOB_STORE': 'jobstore.db',
    'SCHEDULER_JOB_DEFAULTS': {'coalesce': False, 'max_instances': 3},
    'SCHEDULER_TIMEZONE': 'Asia/Shanghai'
}
