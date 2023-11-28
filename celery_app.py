# celery_app.py
from flask import Flask
from celery import Celery

def make_celery(app_name=__name__):
    app = Flask(app_name)
    app.config.update(
        CELERY_BROKER_URL='redis://redis:6379/0',
        CELERY_RESULT_BACKEND='redis://redis:6379/0',
        CELERY_TASK_IGNORE_RESULT=True,
    )

    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)

    return celery

celery = make_celery()

from tasks import my_background_task