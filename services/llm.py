import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

load_dotenv()

class LLM:
    def __init__(self, task_prompt_template):
        self.prompt_template = PromptTemplate(
            input_variables=["task_description"],
            template=task_prompt_template,
        )
        self.llm = OpenAI(openai_api_key=os.environ.get('OPENAI_API_KEY'), temperature=0.9)

    def call(self, task_description):
        prompt_text = self.prompt_template.format(task_description=task_description)
        return self.llm(prompt_text)
