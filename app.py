# In app.py
import os
from flask import Flask
from flask_pymongo import PyMongo
from flasgger import Swagger

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get('MONGO_URI')  # Make sure this points to your MongoDB
app.debug = True
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}

swagger = Swagger(app, config=swagger_config)

mongo = PyMongo(app)

# Import controllers after initializing Flask app and mongo
from controllers.contexts.files_controller import create_file, delete_file 
from controllers.tasks_controller import create_task, show_task
from controllers.health_controller import index_health

# URL route definitions
app.add_url_rule('/tasks/<task_id>', view_func=show_task, methods=['GET'])
app.add_url_rule('/tasks', view_func=create_task, methods=['POST'])
app.add_url_rule('/contexts/files', view_func=create_file, methods=['POST'])
app.add_url_rule('/contents/files/<file_id>', view_func=delete_file, methods=['DELETE'])
app.add_url_rule('/health', view_func=index_health, methods=['GET'])
app.add_url_rule('/', view_func=index_health, methods=['GET'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)