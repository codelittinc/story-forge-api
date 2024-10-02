from bson.objectid import ObjectId
from app import mongo
from models.model import Model

class File(Model):
    @classmethod
    def find_by_id(cls, id):
        document = mongo.db.files.find_one({"_id": ObjectId(id)})
        if document:
            return cls(cls.convert_to_jsonable(document))
        return None
    
    @classmethod
    def delete_by_id(cls, id):
        result = mongo.db.files.delete_one({"_id": ObjectId(id)})
        return result

    @classmethod
    def create(cls, file):
        result = mongo.db.files.insert_one(file)
        inserted_id = result.inserted_id
        inserted_file = mongo.db.files.find_one({'_id': inserted_id})
        return cls(cls.convert_to_jsonable(inserted_file))

    @classmethod
    def find(cls, query):
        documents = mongo.db.files.find(query)
        result = [cls(cls.convert_to_jsonable(document)) for document in documents]
        return result

    def update(self, update_data):
        mongo.db.files.update_one({'_id': ObjectId(self._id)}, {'$set': update_data})
        return File.find_by_id(self._id)

    
