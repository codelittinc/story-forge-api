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
    def create(self, content, context_id):
      
      client = MongoClient(MONGO_URI)
      
      MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]
      
      text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
      docs = text_splitter.split_text(content)

      MongoDBAtlasVectorSearch.from_texts(
          texts=docs,
          embedding=OpenAIEmbeddings(disallowed_special=()),
          collection=MONGODB_COLLECTION,
          index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
          metadatas=[{"context_id": context_id}],
      )

    def get(self, query, context_id):
      vector_search = MongoDBAtlasVectorSearch.from_connection_string(
          MONGO_URI,
          DB_NAME + "." + COLLECTION_NAME,
          OpenAIEmbeddings(disallowed_special=()),
          index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
      )

      # Assuming the field in the documents that stores the context_id is named 'context_id'
      search_filter = {"context_id": context_id}
      
      # Execute the search with the additional filter
      search_type = "similarity"  # Replace with the appropriate search type for your use case

      results = vector_search.search(query, pre_filter={"context_id": {"$eq": context_id}}, search_type="similarity")

      return results