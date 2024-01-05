from dotenv import load_dotenv
import os
load_dotenv()

from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_URI"] = os.environ.get('MONGO_URI')  # Update this URI to point to your MongoDB instance

app.debug = True

mongo = PyMongo(app)

if __name__ == '__main__':
  from controllers.contexts.files_controller import create_file, delete_file 
  from controllers.tasks_controller import create_task, show_task
  from controllers.health_controller import index_health

  app.add_url_rule('/tasks/<task_id>', view_func=show_task, methods=['GET'])
  app.add_url_rule('/tasks', view_func=create_task, methods=['POST'])

  app.add_url_rule('/contexts/files', view_func=create_file, methods=['POST'])
  app.add_url_rule('/contents/files/<file_id>', view_func=delete_file, methods=['DELETE'])

  app.add_url_rule('/health', view_func=index_health, methods=['GET'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)