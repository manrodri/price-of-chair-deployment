import os
from typing import Dict, List
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError


class Dynamodb:

    def __init__(self, table, profile, endpoint_url=None):
        self.session = boto3.Session(profile_name=profile)
        if endpoint_url:
            self.client = self.session.resource('dynamodb', endpoint_url=endpoint_url)
        else:
            self.client = self.session.resource('dynamodb')
        self.table = self.client.Table(table)

    def insert(self, item: Dict) -> Dict:
        self.table.put_item(
            Item=item
        )

        return item

    def delete(self, key_dict: Dict) -> None:
        try:
            self.table.delete_item(Key=key_dict)
        except ClientError as e:
            if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                print(e.response['Error']['Message'])
            else:
                raise ClientError

    def find_by_hash_key(self, hash_key_name, hash_key_value) -> List:
        try:
            response = self.table.query(
                KeyConditionExpression=Key(hash_key_name).eq(hash_key_value)
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            raise ClientError
        else:
            if len(response["Items"]) == 0:
                raise IndexError

            return response['Items']

    def find_by_hash_and_sort_key(self, hash_key_tuple, sort_key_tuple):
        try:
            response = self.table.get_item(
                Key={hash_key_tuple[0]: hash_key_tuple[1], sort_key_tuple[0]: sort_key_tuple[1]})
        except ClientError as e:
            print(e.response['Error']['Message'])
            raise ClientError
        else:
            return response['Item']

    def find_by_index(self, index_name: str, key_tuple: tuple) -> List:
        """

        :param index_name: global secondary index name
        :param key_tuple: (hash_key name, hash_key_value)
        :return: Items matching the query
        """
        try:
            response = self.table.query(
                IndexName=index_name,
                KeyConditionExpression=Key(key_tuple[0]).eq(key_tuple[1]),
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            raise ClientError

        return response['Items']

    def all(self):
        try:
            response = self.table.scan()
        except ClientError as e:
            print(e.response['Error']['Message'])
            raise ClientError

        return response['Items']



    def update(self, key: Dict, update_expression: str, expression_attribute_values: Dict,
               return_values: str = None) -> Dict:
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
