from bson import ObjectId
from flask import jsonify, request, abort

def show_task(task_id):
    from app import mongo
    item = mongo.db.execution_queue.find_one({"_id": ObjectId(task_id)})

    if item:
        item['_id'] = str(item['_id'])
        return jsonify(item)
    else:
        abort(404)

def create_task():
    from celery_app import llm_execution_task
    from app import mongo
    print("aaa")
    if not request.json or 'description' not in request.json:
      abort(400, description="Missing 'description' in request body")

    if not request.json or 'webhook_url' not in request.json:
      abort(400, description="Missing 'webhook_url' in request body")

    if not request.json or 'prompt' not in request.json:
      abort(400, description="Missing 'prompt' in request body")

    print("bbbb")
    if not request.json or 'context_id' not in request.json:
      abort(400, description="Missing 'context_id' in request body")

    if not request.json or 'session_id' not in request.json:
      abort(400, description="Missing 'session' in request body")

    print("cccc")
    item = mongo.db.execution_queue.insert_one({
        "description": request.json['description'],
        "webhook_url": request.json['webhook_url'],
        "prompt": {
           "template": request.json['prompt']['template'],
        },
        "status": "PENDING",
        "context_id": request.json['context_id'],
        "session_id": request.json['session_id'],
    })
    print("ddd")

    item_id = str(item.inserted_id)

    llm_execution_task.delay(item_id)
    print("fff")
    
    return {
       "task_id": item_id 
    }, 200