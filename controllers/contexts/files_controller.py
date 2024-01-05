import os
from flask import jsonify, request, abort
from werkzeug.utils import secure_filename
from services.box import Box
from models.file import File
from celery_app import file_content_task

def delete_file(file_id):
    file = File.find_by_id(file_id)
    Box().delete(file['box_id'])
    delete_result = File.delete_by_id(file_id)

    if delete_result.deleted_count > 0:
      return jsonify(), 204
    else:
      return jsonify(), 404

def create_file():
    if 'file' not in request.files:
        abort(400, description="No file part in the request")

    file = request.files['file']
    if file.filename == '':
        abort(400, description="No selected file")

    if 'context_id' not in request.form:
        abort(400, description="Missing 'context_id' in request")

    if 'webhook_url' not in request.form:
        abort(400, description="Missing 'webhook_url' in request")

    context_id = request.form['context_id']
    filename = secure_filename(file.filename)

    file.save(filename)
    box_file = Box().store(context_id, filename)
    os.remove(filename)

    file_data = {
       **box_file,
        "context_id": context_id,
        "processing": {
            "webhook_url": request.form['webhook_url'],
            "state": "pending",
        }
    }

    file = File.create(file_data)

    file_content_task.delay(file._id)

    return file.to_json(), 200