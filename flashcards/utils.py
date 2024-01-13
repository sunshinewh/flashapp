from pymongo import MongoClient
from django.conf import settings
from bson.objectid import ObjectId

def mongo_handler():
    client = MongoClient(f'mongodb://{settings.MONGO_USER}:{settings.MONGO_PASSWORD}@{settings.MONGO_HOST}/{settings.MONGO_DB}')
    return client[settings.MONGO_DB][settings.MONGO_COLLECTION]

def set_primary_image(card_id, new_image_path):
    collection = mongo_handler()
    query = {'_id': ObjectId(card_id)}
    updated_card = {"$set": {'primary_image': new_image_path}}
    collection.update_one(query, updated_card)
    return
