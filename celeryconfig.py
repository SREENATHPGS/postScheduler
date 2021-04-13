from celery.schedules import crontab

CELERY_IMPORTS = ('scheduler.tasks.process_maker')
CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = 'UTC'

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERYBEAT_SCHEDULE = {
    'test-celery': {
        'task': 'scheduler.tasks.process_maker.create_processes',
        # Every minute
        'schedule': crontab(minute="*"),
    }
}