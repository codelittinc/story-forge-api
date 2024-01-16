from bson import ObjectId
from flask import jsonify, request, abort, Blueprint
tasks_blueprint = Blueprint('files', __name__)

@tasks_blueprint.route('/tasks/<task_id>', methods=['GET'])
def show_task(task_id):
    """
    Retrieves the details of a specific task based on the task ID provided.
    ---
    tags:
      - Tasks
    parameters:
      - in: path
        name: task_id
        required: true
        type: string
        description: The unique identifier of the task.
    responses:
      200:
        description: Details of the task.
        schema:
          type: object
          properties:
            _id:
              type: string
              description: The unique identifier of the task.
            task_description:
              type: string
              description: The description of the task.
            prompt:
              type: object
              description: The prompt template for the task.
              properties:
                template:
                  type: string
                  description: The template string of the prompt.
            processing:
              type: object
              description: Processing details of the task.
              properties:
                status:
                  type: string
                  description: The current status of the task.
                callback_url:
                  type: string
                  description: The callback URL to be triggered upon task completion.
            context_id:
              type: string
              description: The context ID associated with the task.
            session_id:
              type: integer
              description: The session ID associated with the task.
      404:
        description: Task not found.
    """
    from app import mongo
    item = mongo.db.execution_queue.find_one({"_id": ObjectId(task_id)})

    if item:
        item['_id'] = str(item['_id'])
        return jsonify(item)
    else:
        abort(404)

@tasks_blueprint.route('/tasks', methods=['POST'])
def create_task():
    """
    Creates a task for execution and processing. It accepts a task description, callback URL, prompt, context ID, and session ID. Upon completion, it triggers a callback to the specified URL.
    ---
    tags:
      - Tasks
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - task_description
            - callback_url
            - prompt
            - context_id
            - session_id
          properties:
            task_description:
              type: string
              description: The description of the task.
            webhook_url:
              type: string
              description: The URL to which the callback will be made upon task completion.
            prompt:
              type: object
              description: The prompt template for the task.
              properties:
                template:
                  type: string
                  description: The template string of the prompt. Example > Previous conversation {chat_history} Given the context {context} answer the question below {task_description}. Answer like Yoda
            context_id:
              type: string
              description: A unique identifier for the context of the task.
            session_id:
              type: integer
              description: A unique identifier for the session.
    responses:
      200:
        description: Successfully created the task.
        schema:
          type: object
          properties:
            task_id:
              type: string
              description: The ID of the created task.
      400:
        description: Invalid request due to missing required fields.
    """


    from celery_app import execute_llm
    from app import mongo
    if not request.json or 'task_description' not in request.json:
      abort(400, description="Missing 'task_description' in request body")

    if not request.json or 'webhook_url' not in request.json:
      abort(400, description="Missing 'webhook_url' in request body")

    if not request.json or 'prompt' not in request.json:
      abort(400, description="Missing 'prompt' in request body")

    if not request.json or 'context_id' not in request.json:
      abort(400, description="Missing 'context_id' in request body")

    if not request.json or 'session_id' not in request.json:
      abort(400, description="Missing 'session' in request body")

    item = mongo.db.execution_queue.insert_one({
        "task_description": request.json['task_description'],
        "prompt": {
           "template": request.json['prompt']['template'],
        },
        "processing": {
           "status": "pending",
           "webhook_url": request.json['webhook_url']
        },
        "context_id": request.json['context_id'],
        "session_id": request.json['session_id'],
    })

    item_id = str(item.inserted_id)

    execute_llm.delay(item_id)
    
    return {
       "task_id": item_id 
    }, 200