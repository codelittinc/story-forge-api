import os
from flask import Flask
from celery import Celery

def make_celery(app_name=__name__):
    app = Flask(app_name)

    celery = Celery(
        app.import_name,
        broker=os.environ.get('REDIS_URL'),
        backend=os.environ.get('REDIS_URL')
    )
    celery.conf.update(app.config)

    return celery

celery = make_celery()

# registering the tasks on Celery
from tasks import llm_execution_task, webhook_task