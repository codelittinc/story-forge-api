import requests
from app import app
from services.embedder import Embedder
from models.query import Query
from celery import shared_task
from pymongo import MongoClient

@shared_task(name='extract_mongodb_query_content', bind=True)
def extract_mongodb_query_content(self, query_id):
    with app.app_context():
        query = Query.find_by_id(query_id)

        text_representation = ""
        try:
            client = MongoClient(query.connection_string)
            db = client.get_default_database()
            collection = db[query.collection]
            result = collection.find({}, {field: 1 for field in query.fields})

            result_string = " | ".join(query.fields) + "\n"
            for doc in result:
                row_values = [str(doc.get(field, '')) for field in query.fields]
                result_string += " | ".join(row_values) + "\n"

            text_representation = result_string

        except Exception as e:
            text_representation = str(e)

        query.update({
            "processing": {
                "state": "in_progress",
                "webhook_url": query.processing['webhook_url'],
            }
        })

        Embedder().create(text_representation, query.context_id, query_id)
        query = query.update({
            "processing": {
                "state": "complete",
                "webhook_url": query.processing['webhook_url'],
            }
        })

        requests.post(query.processing['webhook_url'], json=query.to_json())
