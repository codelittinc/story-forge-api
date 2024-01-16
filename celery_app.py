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
from tasks.webhooks import send_webhook
from tasks.execute_llm import execute_llm
from tasks.queries import extract_query_content
from tasks.files import extract_file_content