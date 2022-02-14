import os
from typing import Dict, List
import boto3
from boto3.dynamodb.conditions import Key


class UserError(Exception):
    def __init__(self, message):
        self.message = message


class UserNotFoundError(UserError):
    pass


class IncorrectPasswordError(UserError):
    pass


class InvalidEmailError(UserError):
    pass


class Dynamodb:

    def __init__(self, table):
        self.session = boto3.Session(profile_name='acg')
        self.client = self.session.resource('dynamodb')
        self.table = self.client.Table(table)

    def insert(self, item: Dict) -> Dict:
        self.table.put_item(
            Item=item
        )

        return item

    def find_by_hash_key(self, hash_key_name, hash_key_value) -> List:
        try:
            response = self.table.query(
                KeyConditionExpression=Key(hash_key_name).eq(hash_key_value)
            )
        except IndexError:
            raise UserNotFoundError

        return response['Items']

    def find_by_sort_key(self, sort_key_name, sort_key_value) -> List:
        response = self.table.query(
            KeyConditionExpression=Key(sort_key_name).eq(sort_key_value)
        )

        return response['Items']

    def update(self, key: Dict, update_expression: str, expression_attribute_values: Dict, return_values: str = None) -> Dict:
        response = self.table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues=return_values
        )
        return response

    def remove(self, key: Dict) -> None:
        self.table.delete_item(
            Key=key

        )
