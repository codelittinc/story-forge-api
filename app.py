from flask import Flask
from controllers.projects_controller import show_projects, show_project, create_project, update_project, delete_project

app = Flask(__name__)

app.add_url_rule('/projects', view_func=show_projects, methods=['GET'])
app.add_url_rule('/projects/<int:project_id>', view_func=show_project, methods=['GET'])
app.add_url_rule('/projects', view_func=create_project, methods=['POST'])
app.add_url_rule('/projects/<int:project_id>', view_func=update_project, methods=['PUT'])
app.add_url_rule('/projects/<int:project_id>', view_func=delete_project, methods=['DELETE'])

if __name__ == '__main__':
    app.run(debug=True)
