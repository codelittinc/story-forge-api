# mongodb_controller.py

from flask import jsonify, request, abort, Blueprint

queries_blueprint = Blueprint('queries/Postgresql', __name__)

def get_query_model():
    from models.query import Query
    return Query

@queries_blueprint.route('/contexts/queries/postgresql', methods=['POST'])
def create_mongodb_query():
    """
    Creates a new query and schedules it for processing against a Mongo database. Upon completion, a callback is triggered to the specified URL.
    ---
    tags:
      - Queries
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - connection_string
            - fields
            - collection
            - context_id
            - webhook_url
          properties:
            connection_string:
              type: string
              description: Connection string for the database.
            fields:
              type: array
              items:
                type: string
              description: Comma separated array with the fields you want to extract.
            collection:
              type: string
              description: The collection name you want to extract information from.
            context_id:
              type: string
              description: Context ID associated with this query.
            webhook_url:
              type: string
              description: Webhook URL to be called after processing is complete.
    responses:
      200:
        description: Successfully created the query and scheduled for processing.
        schema:
          type: object
          properties:
            _id:
              type: string
              description: The unique identifier of the created query.
            fields:
              type: array
              items:
                type: string
            collection:
              type: string
            connection_string:
              type: string
            context_id:
              type: string
            processing:
              type: object
              properties:
                state:
                  type: string
                  description: Current state of the query processing.
                webhook_url:
                  type: string
      400:
        description: Invalid request due to missing required fields or unsupported database type.
    """


    from celery_app import extract_mongodb_query_content
    required_fields = [ 'connection_string', 'fields', 'collection', 'context_id']
    for field in required_fields:
        if not request.json or field not in request.json:
            abort(400, description=f"Missing '{field}' in request body")

    data = request.json
    connection_string = data.get('connection_string')
    fields = data.get('fields')
    collection = data.get('collection')

    record = get_query_model().create({
        'connection_string': connection_string,
        'fields': fields,
        'collection': collection,
        'context_id': data.get('context_id'),
        'processing': {
            'state': 'pending',
            'webhook_url': data.get('webhook_url')
        }
    })

    extract_mongodb_query_content.delay(record._id)
    
    return jsonify(record.to_json())


# Define your endpoint for deleting queries
@queries_blueprint.route('/contexts/queries/mongodb', methods=['DELETE'])
def delete_query(query_id):
    """
    Deletes a query based on the specified query ID. This endpoint removes the query from the database and any associated records.
    ---
    tags:
      - Queries
    parameters:
      - in: path
        name: query_id
        required: true
        type: string
        description: The unique identifier of the query to delete.
    responses:
      204:
        description: The query was successfully deleted.
      404:
        description: The query with the specified ID was not found or could not be deleted.
    """
    from app import mongo
    query = get_query_model().find_by_id(query_id)

    deleted = False
    if query:
      delete_result = get_query_model().delete_by_id(query_id)
      mongo.db.contents.delete_many({"source_id": query_id})
      deleted = delete_result.deleted_count > 0

    if deleted:
      return jsonify(), 204
    else:
      return jsonify(), 404