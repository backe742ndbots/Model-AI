# from client import get_properties_collection
from db.mongo.client import get_properties_collection



collection = get_properties_collection()
print("Connected. Collection name:", collection.name)
