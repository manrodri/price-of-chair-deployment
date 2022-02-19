import json
from dataclasses import dataclass, field
from typing import List, Dict
import uuid
# from libs.mailgun import Mailgun
from models.item_dynamo import Item
from models.user_dynamo import User
from common.dynamo import Dynamodb


class AlertsError(BaseException):
    def __init__(self, message):
        self.message = message


class AlertNotFound(AlertsError):
    pass


@dataclass(eq=False)
class Alert:
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

    # def notify_if_price_reached(self) -> None:
    #     if self.item.price < self.price_limit:
    #         print(
    #             f"Item {self.item} has reached a price under {self.price_limit}. Latest price: {self.item.price}."
    #         )
    #         Mailgun.send_email(
    #             email=[self.user_email],
    #             subject=f"Notification for {self.name}",
    #             text=f"Your alert {self.name} has reached a price under {self.price_limit}. The latest price is {self.item.price}. Go to this address to check your item: {self.item.url}.",
    #             html=f'<p>Your alert {self.name} has reached a price under {self.price_limit}.</p><p>The latest price is {self.item.price}. Check your item out <a href="{self.item.url}>here</a>.</p>',
    #         )

    @classmethod
    def find_by_email(cls, email):
        try:
            alert_table = Dynamodb(cls.table, "jenkins")
            alerts = alert_table.find_by_hash_key("user_email", email)
            if len(alerts) == 0:
                raise IndexError
            return cls(**cls.create_item(alerts[0]))
        except IndexError:
            raise AlertNotFound('A item with this _id was not found.')

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
        user_table = Dynamodb(cls.table, "jenkins")
        user_table.insert(item)
