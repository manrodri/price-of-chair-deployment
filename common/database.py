import os
from typing import Dict
import pymongo

class Database:

    URI = os.environ['DB_URL']
    DATABASE = pymongo.MongoClient(URI).get_default_database()

    @staticmethod
    def insert(collection: str, data: Dict) -> None:
        Database.DATABASE[collection].insert_one(data)

    @staticmethod
    def find(collection: str, query: Dict) -> pymongo.cursor:
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection: str, query: Dict) -> Dict:
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def update(collection: str, query: Dict, data: Dict) -> None:
        # {"$set": {"some_field": "some update"}}
        query_data = {"$set": data}
        Database.DATABASE[collection].update_one(query, query_data, upsert=True)

    @staticmethod
    def remove(collection: str, query: Dict):
        Database.DATABASE[collection].find_one_and_delete(query)
