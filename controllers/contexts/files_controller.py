import os
from flask import jsonify, request, abort, Blueprint
from werkzeug.utils import secure_filename
from services.box import Box

files_blueprint = Blueprint('files', __name__)

def get_file_model():
    from models.file import File
    return File

def delete_file(file_id):
    """
    Deletes a file with the given ID. This includes removing the file from storage and deleting any related records in the database.
    ---
    tags:
      - Files
    parameters:
      - in: path
        name: file_id
        type: string
        required: true
        description: The ID of the file to delete.
    responses:
      204:
        description: The file was successfully deleted.
      404:
        description: The file with the specified ID was not found or could not be deleted.
    """
    from app import mongo
    file = get_file_model().find_by_id(file_id)

    deleted = False
    if file:
      Box().delete(file.box_id)
      delete_result = get_file_model().delete_by_id(file_id)
      mongo.db.contents.delete_many({"source_id": file_id})
      deleted = delete_result.deleted_count > 0

    if deleted:
      return jsonify(), 204
    else:
      return jsonify(), 404

@files_blueprint.route('/contexts/files', methods=['POST'])
def create_file():
    """
    This is an endpoint that creates a file and stores it. Once it is processed, it will send a webhook to the URL provided.
    ---
    tags:
      - Files
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: The file to upload.
      - in: formData
        name: context_id
        type: string
        required: true
        description: The context ID for the file.
      - in: formData
        name: webhook_url
        type: string
        required: true
        description: The webhook URL to notify once processing is complete.
    responses:
      200:
        description: Upon completion of file processing, a webhook is sent with the payload below.
        schema:
          type: object
          properties:
            filename:
              type: string
            context_id:
              type: string
            file_extension:
              type: string
            id:
              type: string
            processing:
              type: object
              properties:
                webhook_url:
                  type: string
                state:
                  type: string
            public_url:
              type: string
        examples:
          application/json: {
            "context_id": "234423",
            "file_extension": "txt",
            "filename": "test_ai.txt",
            "id": "65a15c781f16a48f7ef93ad5",
            "processing": {
              "state": "pending",
              "webhook_url": "https://webhook.site/2e6af978-9229-4a66-80fe-sdfdsfdsfsdf"
            },
            "public_url": "https://codelitt.box.com/shared/static/sdfdsfdsfsdfdsfds.txt"
          }
    """
    from celery_app import extract_file_content 

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

    extract_file_content(file._id)
    response = file.to_json()
    del response['box_id']
    del response['stored_filename']
    response['filename'] = response['original_filename']
    del response['original_filename']
    return response, 200