from flask import jsonify, request, abort, Blueprint

queries_blueprint = Blueprint('queries', __name__)

def get_query_model():
    from models.query import Query
    return Query

@queries_blueprint.route('/contexts/queries', methods=['POST'])
def create_query():
    """
    Creates a new query and schedules it for processing against a PostgreSQL database. Upon completion, a callback is triggered to the specified URL.
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
            - database_type
            - connection_string
            - query
            - context_id
            - webhook_url
          properties:
            database_type:
              type: string
              description: Type of the database (only 'postgres' is supported).
            connection_string:
              type: string
              description: Connection string for the database.
            query:
              type: string
              description: SQL query to be executed.
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
            database_type:
              type: string
            connection_string:
              type: string
            query:
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

    from celery_app import extract_query_content
    required_fields = ['database_type', 'connection_string', 'query', 'context_id']
    for field in required_fields:
        if not request.json or field not in request.json:
            abort(400, description=f"Missing '{field}' in request body")

    data = request.json
    database_type = data.get('database_type')
    connection_string = data.get('connection_string')
    query = data.get('query')

    if database_type.lower() != 'postgres':
        return jsonify({"error": "Unsupported database type"}), 400

    record = get_query_model().create({
        'database_type': database_type,
        'connection_string': connection_string,
        'query': query,
        'context_id': data.get('context_id'),
        'processing': {
            'state': 'pending',
            'webhook_url': data.get('webhook_url')
        }
    })
    extract_query_content.delay(record._id)
    
    return jsonify(record.to_json())


# Define your endpoint for deleting queries
@queries_blueprint.route('/contexts/queries', methods=['DELETE'])
def delete_query(query_id):
    from app import mongo
    query = get_query_model().find_by_id(query_id)

    deleted = False
    if query:
      delete_result = get_query_model().delete_by_id(query_id)
      mongo.db.contents.delete_many({"query_id": query_id})
      deleted = delete_result.deleted_count > 0

    if deleted:
      return jsonify(), 204
    else:
      return jsonify(), 404