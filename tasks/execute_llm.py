from celery_app import celery
from bson import ObjectId
from app import mongo, app
from services.llm import LLM
from services.embedder import Embedder
from tasks.webhooks import send_webhook

@celery.task(name='execute_llm')
def execute_llm(item_id):
    with app.app_context():
      item = mongo.db.execution_queue.find_one({"_id": ObjectId(item_id)})

      task_description = item['task_description']
      prompt_template = item['prompt']['template']
      context_id = item['context_id']
      session_id = item['session_id']

      results = Embedder().get(task_description, context_id)

      context = ""
      for result in results:
          context += result.page_content + "\n"
      
      llm_service = LLM(prompt_template)

      result = llm_service.call(task_description, context, session_id)
      answer = result['answer'] 
      prompt = result['prompt']
    
      mongo.db.execution_queue.update_one({"_id": ObjectId(item_id)}, {"$set": {
         "response": answer,
         "processing": {
              "status": "complete",
              "webhook_url": item['processing']['webhook_url']
         },
         "prompt": {
            "template": prompt_template,
            "parsed": prompt
         }
       }})

      send_webhook.delay(item_id)
