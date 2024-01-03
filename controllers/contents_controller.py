from app import mongo
from flask import jsonify, request, abort
from services.embedder import Embedder

def delete_all_contents():
    result = mongo.db.contents.delete_many({})

    if result.deleted_count > 0:
      return jsonify({"message": f"Deleted {result.deleted_count} items."})
    else:
      return jsonify({"message": "No items to delete."})

def create_content():
    if not request.json or 'text' not in request.json:
      abort(400, description="Missing 'text' in request body")

    if not request.json or 'context_id' not in request.json:
      abort(400, description="Missing 'context_id' in request body")
    
    Embedder().create(request.json['text'], request.json['context_id'])

    return {
       "response":  "content added successfuly"
    }, 200