from typing import List, Dict, TypeVar, Type
from abc import ABCMeta, abstractmethod
from common.dynamo import Dynamodb

T = TypeVar('T')


class Model(metaclass=ABCMeta):
    table: str
    _id: str

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def save_to_dynamo(cls, item: Dict) -> "T":
        return cls(**Dynamodb(cls.table, "jenkins").insert(item))

    @classmethod
    def remove_from_dynamo(cls, key_dict: Dict) -> None:
        Dynamodb(cls.table, "jenkins").delete(key_dict)

    @abstractmethod
    def json(self) -> Dict:
        raise NotImplementedError

    @abstractmethod
    def create_item(self, item: Dict) -> Dict:
        raise NotImplementedError

    @classmethod
    def all(cls) -> List:
        return Dynamodb(cls.table, "jenkins").all()
