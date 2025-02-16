import os
import ssl
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

    # Configure SSL for the broker and backend if using rediss://
    ssl_options = {'ssl_cert_reqs': ssl.CERT_REQUIRED}
    celery.conf.broker_use_ssl = ssl_options
    celery.conf.redis_backend_use_ssl = ssl_options

    return celery

celery = make_celery()

# registering the tasks on Celery
from tasks.webhooks import send_webhook
from tasks.execute_llm import execute_llm
from tasks.postgresql_query import extract_postgresql_query_content
from tasks.files import extract_file_content
from tasks.mongodb_query import extract_mongodb_query_content
