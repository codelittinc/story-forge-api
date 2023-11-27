from flask import jsonify, request, abort

# This could alternatively be a database or some other persistence mechanism
projects = [
    {"id": 1, "name": "Project 1", "description": "A sample project"},
    # ... other projects
]

def show_projects():
    return jsonify(projects)

def show_project(project_id):
    project = next((project for project in projects if project['id'] == project_id), None)
    return jsonify(project) if project else abort(404)

def create_project():
    return projects[0], 201

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
