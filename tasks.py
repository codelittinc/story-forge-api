from celery_app import celery
from bson import ObjectId
import requests
from app import mongo
from services.llm import LLM

@celery.task(name='my_background_task')
def my_background_task(item_id):
    item = mongo.db.execution_queue.find_one({"_id": ObjectId(item_id)})
    llm_service = LLM()

    description = item['description']
    webhook_url = item['webhook_url']

    result = llm_service.call(description)

    response = requests.post(webhook_url, json={'description': result})

    if response.status_code != 200:
        print(f'POST to {webhook_url} failed with status code {response.status_code}.')
    else:
        print(f'Successfully posted to {webhook_url}.')