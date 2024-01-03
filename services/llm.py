import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

load_dotenv()

class LLM:
    def __init__(self, prompt_template, prompt_variables):
        self.prompt_template = PromptTemplate(
            input_variables=prompt_variables,
            template=prompt_template,
        )
        self.llm = OpenAI(openai_api_key=os.environ.get('OPENAI_API_KEY'), temperature=0.9)

    def call(self, task_description, context):
        prompt_text = self.prompt_template.format(task_description=task_description, context=context)
        return self.llm(prompt_text)
