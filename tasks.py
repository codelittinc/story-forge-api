from celery_app import celery
from bson import ObjectId
import json
from datetime import datetime
import requests
from app import mongo, app
from services.llm import LLM
from services.embedder import Embedder
from services.box import Box
from models.file import File
from models.query import Query
from celery import shared_task
from celery.exceptions import Retry
import psycopg2

def default_converter(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError("Object of type '%s' is not JSON serializable" % type(o).__name__)


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
          if 'box_id' in item:
              del item['box_id']
          if 'stored_filename' in item:
              del item['stored_filename']
          if 'original_filename' in item:
              item['filename'] = item['original_filename']
              del item['original_filename']
          item['id'] = str(item['_id'])
          del item['_id']

          json_data = json.dumps(item)
          json_data = json.loads(json_data)

      response = requests.post(webhook_url, json=json_data)

      webhook_object = {
          "status": response.status_code,
          "response": response.text,
          "webhook_url": webhook_url
      }
    
      mongo.db.execution_queue.update_one({"_id": ObjectId(item_id)}, {"$push": {"webhook_requests": webhook_object}})

# @TODO: update how we save about the webhook processing
#      if response.status_code == 200:
#        mongo.db.execution_queue.update_one({"_id": ObjectId(item_id)}, {"$set": {"status": "PROCESSED"}})
#      else:
#        mongo.db.execution_queue.update_one({"_id": ObjectId(item_id)}, {"$set": {"status": "WEBHOOK_ERROR"}})

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

    json = file.to_json()
    del json['box_id']

    requests.post(file.processing['webhook_url'], json=file.to_json())

@shared_task(name='query_content_task', bind=True)
def query_content_task(self, query_id):
    with app.app_context():
      query = Query.find_by_id(query_id)

      text_representation = ""
      try:
          conn = psycopg2.connect(query.connection_string)
          cursor = conn.cursor()
          cursor.execute(query.query)
          result = cursor.fetchall()
          columns = [desc[0] for desc in cursor.description]
          cursor.close()
          conn.commit()
          conn.close()

          result_string = " | ".join(columns) + "\n"
          
          for row in result:
              row_values = [str(value) for value in row]
              result_string += " | ".join(row_values) + "\n"
          

          text_representation = result_string
      except Exception as e:
          text_representation = str(e)
     
      query.update({
          "processing": {
            "state": "in_progress",
            "webhook_url": query.processing['webhook_url'],
          }
      })
      
      Embedder().create(text_representation, query.context_id, query_id)
      query = query.update({
          "processing": {
            "state": "complete",
            "webhook_url": query.processing['webhook_url'],
          }
      })

      requests.post(query.processing['webhook_url'], json=query.to_json())