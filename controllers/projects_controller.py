from flask import jsonify, request, abort, current_app
from services.llm import LLM
from celery_app import my_background_task
from app import mongo  # Import the mongo instance directly


projects = [
    {"id": 1, "name": "Project 1", "description": "A sample project"},
]

def show_project(project_id):
    project = next((project for project in projects if project['id'] == project_id), None)
    return jsonify(project) if project else abort(404)

def create_project():
    if not request.json or 'description' not in request.json:
      abort(400, description="Missing 'description' in request body")


    result = mongo.db.projects.insert_one(projects[0])

    my_background_task.delay(123, 345)

    description = request.json['description']
    llm_service = LLM()

#    result = llm_service.call(description)
    return {
       "id": str(result.inserted_id)
    }, 200