from dataclasses import dataclass, field
import uuid
import re
from typing import Dict, List
import json

from common.dynamo import Dynamodb


class StoresErrors(BaseException):
    def __init__(self, message):
        self.message = message


class StoreNotFound(StoresErrors):
    pass


@dataclass(eq=False)
class Store:
    table: str = field(init=False, default="Stores")
    name: str
    url_prefix: str
    tag_name: str
    query: Dict
    _id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def json(self) -> Dict:
        return {
            "_id": self._id,
            "name": self.name,
            "url_prefix": self.url_prefix,
            "tag_name": self.tag_name,
            "query": json.dumps(self.query)
        }

    @classmethod
    def get_by_name(cls, store_name: str) -> "Store":
        try:
            store_table = Dynamodb(cls.table, "jenkins")
            stores = store_table.find_by_index('name-index', ("name", store_name))
            if len(stores) == 0:
                raise IndexError
        except IndexError:
            raise StoreNotFound(f'A store with this name: {store_name} was not found.')

        # todo: Store name must be unique
        return cls(**cls.create_item(stores[0]))

    @classmethod
    def get_by_url_prefix(cls, url_prefix: str) -> "Store":
        store_table = Dynamodb(cls.table, "jenkins")
        try:
            stores = store_table.find_by_hash_key("url_prefix", url_prefix)
            if len(stores) == 0:
                raise IndexError
            return cls(**cls.create_item(stores[0]))
        except IndexError:
            raise StoreNotFound(f'A store with this name: {url_prefix} was not found.')

    @classmethod
    def find_by_url(cls, url: str) -> "Store":
        """
        Return a store from a url like "http://www.johnlewis.com/item/sdfj4h5g4g21k.html"
        :param url: The item's URL
        :return: a Store
        """
        pattern = re.compile(r"(https?:\/\/.*?\/)")
        match = pattern.search(url)
        url_prefix = match.group(1)
        return cls.get_by_url_prefix(url_prefix)

    @classmethod
    def create_item(cls, item_from_dynamo):
        return {
            "_id": item_from_dynamo['_id'],
            "name": item_from_dynamo["name"],
            "tag_name": item_from_dynamo["tag_name"],
            "url_prefix": item_from_dynamo['url_prefix'],
            "query": json.loads(item_from_dynamo['query'])
        }

    @classmethod
    def save_to_dynamo(cls, item: Dict) -> None:
        user_table = Dynamodb(cls.table, "jenkins")
        user_table.insert(item)

    @classmethod
    def all(cls) -> List:
        store_table = Dynamodb(cls.table, "jenkins")
        return store_table.all()
