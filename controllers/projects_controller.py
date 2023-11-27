from flask import jsonify, request, abort
from services.llm import LLM

projects = [
    {"id": 1, "name": "Project 1", "description": "A sample project"},
]

def show_projects():
    return jsonify(projects)

def show_project(project_id):
    project = next((project for project in projects if project['id'] == project_id), None)
    return jsonify(project) if project else abort(404)

def create_project():
    if not request.json or 'description' not in request.json:
      abort(400, description="Missing 'description' in request body")

    # Extract the description from the request
    description = request.json['description']
    llm_service = LLM()

    result = llm_service.call(description)
    return result, 200

def update_project(project_id):
    project = next((project for project in projects if project['id'] == project_id), None)
    if not project:
        abort(404)
    if not request.json:
        abort(400)
    project['name'] = request.json.get('name', project['name'])
    project['description'] = request.json.get('description', project['description'])
    return jsonify(project)

def delete_project(project_id):
    global projects
    project = next((project for project in projects if project['id'] == project_id), None)
    if not project:
        abort(404)
    projects = [project for project in projects if project['id'] != project_id]
    return jsonify({'result': True})
