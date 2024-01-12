from bson.objectid import ObjectId

class Model:
    def __init__(self, attrs=None):
        if attrs:
            for key, value in attrs.items():
                setattr(self, key, value)

    @classmethod
    def convert_to_jsonable(self, data):
        """ Convert MongoDB document to a JSON serializable format """
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, ObjectId):
                    data[key] = str(value)
        return data

    def to_json(self):
        """ Convert the model instance into a JSON serializable dictionary """
        jsonable_data = {}
        for attribute, value in self.__dict__.items():
            # If the value is an ObjectId, convert it to string
            if attribute == '_id':
                jsonable_data['id'] = str(value)
            else:
                jsonable_data[attribute] = value
        return jsonable_data
