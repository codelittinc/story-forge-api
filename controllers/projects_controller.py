from flask import jsonify, request, abort
from services.llm import LLM

projects = [
    {"id": 1, "name": "Project 1", "description": "A sample project"},
]

def show_project(project_id):
    project = next((project for project in projects if project['id'] == project_id), None)
    return jsonify(project) if project else abort(404)

def create_project():
    if not request.json or 'description' not in request.json:
      abort(400, description="Missing 'description' in request body")

    description = request.json['description']
    llm_service = LLM()

    result = llm_service.call(description)
    return {
       "userStories": result
    }, 200