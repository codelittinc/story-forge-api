web: gunicorn -w 4 --log-level debug app:app
flower: celery flower --persistent=True --port=$PORT
worker: celery -A celery_app.celery worker --loglevel=debug --concurrency 2