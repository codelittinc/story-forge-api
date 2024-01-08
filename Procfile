web: gunicorn -w 4 --log-level debug app:app
worker: celery -A celery_app.celery worker --loglevel=debug --concurrency 2