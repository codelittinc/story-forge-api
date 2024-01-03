import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pymongo import MongoClient
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_community.embeddings import OpenAIEmbeddings

load_dotenv()

DB_NAME = "storyforge"
COLLECTION_NAME = "contents"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "testing-still"
MONGO_URI = os.environ.get('MONGO_URI')

class Embedder:
    def create(self, content):
      
      client = MongoClient(MONGO_URI)
      
      MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]
      
      text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
      docs = text_splitter.split_text(content)

      MongoDBAtlasVectorSearch.from_texts(
          texts=docs,
          embedding=OpenAIEmbeddings(disallowed_special=()),
          collection=MONGODB_COLLECTION,
          index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
      )

    def get(self, query):
      vector_search = MongoDBAtlasVectorSearch.from_connection_string(
          MONGO_URI,
          DB_NAME + "." + COLLECTION_NAME,
          OpenAIEmbeddings(disallowed_special=()),
          index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
      )

      results = vector_search.similarity_search(query)
      return results