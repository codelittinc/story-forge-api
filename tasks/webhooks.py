from celery_app import celery
from bson import ObjectId
import json
import requests
from app import mongo, app

@celery.task(name='send_webhook')
def send_webhook(item_id):
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