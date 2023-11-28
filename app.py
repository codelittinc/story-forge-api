from flask import Flask
from controllers.projects_controller import show_project, create_project
from controllers.health_controller import index_health

app = Flask(__name__)

app.add_url_rule('/projects/<int:project_id>', view_func=show_project, methods=['GET'])
app.add_url_rule('/projects', view_func=create_project, methods=['POST'])

app.add_url_rule('/health', view_func=index_health, methods=['GET'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
