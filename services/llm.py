import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import MongoDBChatMessageHistory

load_dotenv()

class LLM:
    def __init__(self, prompt_template):
        # Set the model to 'gpt-4'
        self.llm = ChatOpenAI(
            openai_api_key=os.environ.get('OPENAI_API_KEY'),
            model='gpt-4o',  # Explicitly set the model to GPT-4
            temperature=0.9
        )
        self.prompt_text = prompt_template

    def call(self, task_description, context, session_id):
        # Initialize chat message history
        history = MongoDBChatMessageHistory(connection_string=os.environ.get('MONGO_URI'), session_id=session_id)

        # Create prompt template
        prompt = PromptTemplate.from_template(self.prompt_text)

        # Set up the conversation chain
        conversation = LLMChain(
            llm=self.llm,
            prompt=prompt,
            verbose=True,
        )

        # Predict the answer
        answer = conversation.predict(task_description=task_description, chat_history=history.messages, context=context)

        # Format the prompt for logging
        prompt_description = prompt.format(task_description=task_description, chat_history=history.messages, context=context)

        # Update the chat history with the latest messages
        history.add_user_message(task_description)
        history.add_ai_message(answer)

        return {
            "answer": answer.strip(),
            "prompt": prompt_description
        }
