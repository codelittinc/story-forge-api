import os
from dotenv import load_dotenv

load_dotenv()

from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

class LLM:
    def __init__(self):
        self.prompt_template = PromptTemplate(
            input_variables=["product_description"],
            template="Below you have a description of a product I want to build. Create the user stories {product_description}",
        )
        self.llm = OpenAI(openai_api_key=os.environ.get('OPENAI_API_KEY'), temperature=0.9)

    def call(self, product_description):
        prompt_text = self.prompt_template.format(product_description=product_description)
        return self.llm(prompt_text)
