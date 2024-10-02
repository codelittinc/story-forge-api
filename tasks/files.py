from datetime import datetime
import requests
from services.embedder import Embedder
from services.box import Box
from models.file import File
from celery import shared_task
from celery.exceptions import Retry

@shared_task(name='extract_file_content', bind=True)
def extract_file_content(self, file_id):
    file = File.find_by_id(file_id)
    text_representation = Box().get_text_representation(file.box_id)

    if text_representation is None:
        try:
            # Retry the task after 3 seconds
            raise self.retry(countdown=3)
        except Retry as exc:
            raise exc  # Reraise the Retry exception to ensure the task is retried
        except Exception as exc:
            # Handle other exceptions that might occur
            raise self.retry(exc=exc, countdown=3)

    file.update({
        "processing": {
          "state": "in_progress",
          "webhook_url": file.processing['webhook_url'],
        }
    })
    
    Embedder().create(text_representation, file.context_id, file_id)
    file = file.update({
        "processing": {
          "state": "complete",
          "webhook_url": file.processing['webhook_url'],
        },
        "text_representation": text_representation
    })

    json = file.to_json()
    del json['box_id']

    requests.post(file.processing['webhook_url'], json=file.to_json())