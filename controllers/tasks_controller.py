from flask import jsonify, request, abort
from celery_app import llm_execution_task
from bson import ObjectId
from app import mongo

def show_task(task_id):
    item = mongo.db.execution_queue.find_one({"_id": ObjectId(task_id)})

    if item:
        item['_id'] = str(item['_id'])
        return jsonify(item)
    else:
        abort(404)

def create_task():
    if not request.json or 'description' not in request.json:
      abort(400, description="Missing 'description' in request body")

    if not request.json or 'webhook_url' not in request.json:
      abort(400, description="Missing 'webhook_url' in request body")

    item = mongo.db.execution_queue.insert_one({
        "description": request.json['description'],
        "webhook_url": request.json['webhook_url'],
        "status": "PENDING"
    })

    item_id = str(item.inserted_id)

    llm_execution_task.delay(item_id)
    
    return {
       "id": item_id 
    }, 200