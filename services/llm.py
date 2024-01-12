import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.memory import MongoDBChatMessageHistory

load_dotenv()

class LLM:
    def __init__(self, prompt_template):
        self.llm = OpenAI(openai_api_key=os.environ.get('OPENAI_API_KEY'), temperature=0.9)
        self.prompt_text = prompt_template

    def call(self, task_description, context, session_id):
        history = MongoDBChatMessageHistory(connection_string=os.environ.get('MONGO_URI'), session_id=session_id)

        prompt = PromptTemplate.from_template(self.prompt_text)

        conversation = LLMChain(
            llm=self.llm,
            prompt=prompt,
            verbose=True,
        )

        answer = conversation.predict(task_description=task_description, chat_history=history.messages, context=context)
        prompt_description = prompt.format(task_description=task_description, chat_history=history.messages, context=context)
        history.add_user_message(task_description)
        history.add_ai_message(answer)

        return {
            "answer": answer.strip(),
            "prompt": prompt_description
        }
