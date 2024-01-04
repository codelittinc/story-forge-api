from celery_app import celery
from flask import jsonify
from bson import ObjectId
import requests
from app import mongo, app
from services.llm import LLM
from services.embedder import Embedder

@celery.task(name='llm_execution_task')
def llm_execution_task(item_id):
    with app.app_context():
      item = mongo.db.execution_queue.find_one({"_id": ObjectId(item_id)})

      description = item['description']
      prompt_template = item['prompt']['template']
      context_id = item['context_id']
      session_id = item['session_id']

      results = Embedder().get(description, context_id)

      context = ""
      for result in results:
          context += result.page_content + "\n"
      
      llm_service = LLM(prompt_template)

      result = llm_service.call(description, context, session_id)
    
      mongo.db.execution_queue.update_one({"_id": ObjectId(item_id)}, {"$set": {"result": result, "status": "LLM_COMPLETED"}})

      webhook_task.delay(item_id)

@celery.task(name='webhook_task')
def webhook_task(item_id):
    with app.app_context():
      item = mongo.db.execution_queue.find_one({"_id": ObjectId(item_id)})

      webhook_url = item['webhook_url']

      if item:
          item['_id'] = str(item['_id'])
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