from dataclasses import dataclass, field
from typing import Dict
from bs4 import BeautifulSoup
import requests
import re
import uuid
import json

from common.dynamo import Dynamodb


class ItemsError(BaseException):
    def __init__(self, message):
        self.message = message


class ItemNotFound(ItemsError):
    pass


@dataclass(eq=False)
class Item:
    table: str = field(init=False, default="Items")
    url: str
    tag_name: str
    query: Dict
    price: float = field(default=None)
    _id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def load_price(self) -> float:
        request = requests.get(self.url)
        content = request.content
        soup = BeautifulSoup(content, "html.parser")
        element = soup.find(self.tag_name, self.query)
        string_price = element.text.strip()

        pattern = re.compile(r"(\d+,?\d+\.\d+)")
        match = pattern.search(string_price)
        found_price = match.group(1)
        without_commas = found_price.replace(",", "")
        self.price = float(without_commas)
        return self.price

    @classmethod
    def save_to_dynamo(cls, item):
        user_table = Dynamodb(cls.table, 'us-east-1')
        user_table.insert(item)

    @classmethod
    def find_by_id(cls, id: str) -> "Item":
        try:
            item_table = Dynamodb(cls.table, 'us-east-1')
            items = item_table.find_by_hash_key("_id", id)
            if len(items) == 0:
                raise IndexError
            return cls(**cls.create_item(items[0]))
        except IndexError:
            raise ItemNotFound('A item with this _id was not found.')

    def json(self) -> Dict:
        return {
            "_id": self._id,
            "url": self.url,
            "tag_name": self.tag_name,
            "price": str(self.price),
            "query": json.dumps(self.query)
        }

    @classmethod
    def create_item(cls, item_from_dynamo):
        return {
            "_id": item_from_dynamo['_id'],
            "url": item_from_dynamo["url"],
            "tag_name": item_from_dynamo["tag_name"],
            "price": float(item_from_dynamo['price']),
            "query": json.loads(item_from_dynamo['query'])
        }
