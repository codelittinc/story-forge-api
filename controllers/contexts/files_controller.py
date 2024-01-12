import os
from flask import jsonify, request, abort
from werkzeug.utils import secure_filename
from services.box import Box

def get_file_model():
    from models.file import File
    return File

def delete_file(file_id):
    from app import mongo
    file = get_file_model().find_by_id(file_id)

    deleted = False
    if file:
      Box().delete(file.box_id)
      delete_result = get_file_model().delete_by_id(file_id)
      mongo.db.contents.delete_many({"file_id": file_id})
      deleted = delete_result.deleted_count > 0

    if deleted:
      return jsonify(), 204
    else:
      return jsonify(), 404

def create_file():
    from celery_app import file_content_task

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

    file = get_file_model().create(file_data)

    file_content_task(file._id)
    response = file.to_json()
    del response['box_id']
    del response['stored_filename']
    response['filename'] = response['original_filename']
    del response['original_filename']
    return response, 200