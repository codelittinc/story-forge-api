from bson.objectid import ObjectId
from app import mongo
from models.model import Model

class Query(Model):
    @classmethod
    def find_by_id(cls, id):
        document = mongo.db.queries.find_one({"_id": ObjectId(id)})
        if document:
            return cls(cls.convert_to_jsonable(document))
        return None
    
    @classmethod
    def delete_by_id(cls, id):
        result = mongo.db.queries.delete_one({"_id": ObjectId(id)})
        return result

    @classmethod
    def create(cls, query):
        result = mongo.db.queries.insert_one(query)
        inserted_id = result.inserted_id
        inserted_query = mongo.db.queries.find_one({'_id': inserted_id})
        return cls(cls.convert_to_jsonable(inserted_query))

    def update(self, update_data):
        mongo.db.queries.update_one({'_id': ObjectId(self._id)}, {'$set': update_data})
        return Query.find_by_id(self._id)

    
