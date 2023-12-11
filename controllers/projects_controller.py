from flask import jsonify, request, abort
from celery_app import my_background_task
from app import mongo

projects = [
    {"id": 1, "name": "Project 1", "description": "A sample project"},
]

def show_project(project_id):
    project = next((project for project in projects if project['id'] == project_id), None)
    return jsonify(project) if project else abort(404)

def create_project():
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

    my_background_task.delay(item_id)
    
    return {
       "id": item_id 
    }, 200