from celery_app import celery
from flask import jsonify
from bson import ObjectId
import requests
from app import mongo, app
from services.llm import LLM
from services.embedder import Embedder
from services.box import Box
from models.file import File
from celery import shared_task
from celery.exceptions import Retry

@celery.task(name='llm_execution_task')
def llm_execution_task(item_id):
    with app.app_context():
      item = mongo.db.execution_queue.find_one({"_id": ObjectId(item_id)})

      task_description = item['task_description']
      prompt_template = item['prompt']['template']
      context_id = item['context_id']
      session_id = item['session_id']

      results = Embedder().get(task_description, context_id)

      context = ""
      for result in results:
          context += result.page_content + "\n"
      
      llm_service = LLM(prompt_template)

      result = llm_service.call(task_description, context, session_id)
      answer = result['answer'] 
      prompt = result['prompt']
    
      mongo.db.execution_queue.update_one({"_id": ObjectId(item_id)}, {"$set": {
         "response": answer,
         "processing": {
              "status": "complete",
              "webhook_url": item['processing']['webhook_url']
         },
         "prompt": {
            "template": prompt_template,
            "parsed": prompt
         }
       }})

      webhook_task.delay(item_id)

@celery.task(name='webhook_task')
def webhook_task(item_id):
    with app.app_context():
      item = mongo.db.execution_queue.find_one({"_id": ObjectId(item_id)})

      webhook_url = item['processing']['webhook_url']

      if item:
          item['id'] = str(item['_id'])
          del item['_id']
          json_data = jsonify(item).get_json()

      response = requests.post(webhook_url, json=json_data)

      webhook_object = {
          "status": response.status_code,
          "response": response.text,
          "webhook_url": webhook_url
      }
    
      mongo.db.execution_queue.update_one({"_id": ObjectId(item_id)}, {"$push": {"webhook_requests": webhook_object}})

      if response.status_code == 200:
        mongo.db.execution_queue.update_one({"_id": ObjectId(item_id)}, {"$set": {"status": "PROCESSED"}})
      else:
        mongo.db.execution_queue.update_one({"_id": ObjectId(item_id)}, {"$set": {"status": "WEBHOOK_ERROR"}})

@shared_task(name='file_content_task', bind=True)
def file_content_task(self, file_id):
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
        }
    })

    requests.post(file.processing['webhook_url'], json=file.to_json())