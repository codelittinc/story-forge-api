import requests
from app import app
from services.embedder import Embedder
from models.query import Query
from celery import shared_task
import psycopg2

@shared_task(name='extract_postgresql_query_content', bind=True)
def extract_postgresql_query_content(self, query_id):
    with app.app_context():
      query = Query.find_by_id(query_id)

      text_representation = ""
      try:
          conn = psycopg2.connect(query.connection_string)
          cursor = conn.cursor()
          cursor.execute(query.query)
          result = cursor.fetchall()
          columns = [desc[0] for desc in cursor.description]
          cursor.close()
          conn.commit()
          conn.close()

          result_string = " | ".join(columns) + "\n"
          
          for row in result:
              row_values = [str(value) for value in row]
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