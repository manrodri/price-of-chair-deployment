from dataclasses import dataclass, field
from typing import List, Dict
import uuid

from models.item_dynamo import Item
from models.model import Model
from models.user_dynamo.user import User
from common.dynamo import Dynamodb


class AlertsError(BaseException):
    def __init__(self, message):
        self.message = message


class AlertNotFound(AlertsError):
    pass


@dataclass(eq=False)
class Alert(Model):
    table: str = field(init=False, default="Alerts")
    name: str
    item_id: str
    price_limit: float
    user_email: str
    _id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def __post_init__(self):
        self.item = Item.find_by_id(self.item_id)
        self.user = User.find_by_email(self.user_email)

    def json(self) -> Dict:
        return {
            "_id": self._id,
            "name": self.name,
            "price_limit": str(self.price_limit),
            "item_id": self.item._id,
            "user_email": self.user_email,
        }

    def load_item_price(self) -> float:
        self.item.load_price()
        return self.item.price

    @classmethod
    def find_by_email(cls, email) -> List["Alert"]:
        try:
            alert_table = Dynamodb(cls.table)
            alerts = alert_table.find_by_hash_key("user_email", email)
            return [cls(**cls.create_item(alert)) for alert in alerts]
        except IndexError:
            return []

    @classmethod
    def find_by_id(cls, id: str, email: str) -> "Alert":
        alert_table =  Dynamodb(cls.table)
        item = alert_table.get_item({"user_email": email, "_id": id})
        return cls(**item)

    @classmethod
    def create_item(cls, item_from_dynamo):
        return {
            "_id": item_from_dynamo['_id'],
            "item_id": item_from_dynamo["item_id"],
            "name": item_from_dynamo["name"],
            "price_limit": float(item_from_dynamo['price_limit']),
            "user_email": item_from_dynamo['user_email']
        }

    @classmethod
    def save_to_dynamo(cls, item):
        user_table = Dynamodb(cls.table)
        user_table.insert(item)
