import json
import boto3
import botostubs

from buy_book.SourceFile import SourceFile, Book, Enchantment

client = boto3.client('s3')
prices_json_path = "buy_book/data/prices.json"


def lambda_handler(event, context):
    """Lambda handler."""
    print(event)
    bucket_name, object_key = get_objectinfo(event)
    json_str = get_object(bucket_name, object_key)
    sourceFile = read_json(json_str)
    return


def get_objectinfo(event: dict):
    """S3イベントからバケット名とオブジェクトキーを取り出す.

    Arguments:
        event {dict} -- S3イベント.

    Returns:
        tuple(str, str) -- バケット名, オブジェクトキー
    """
    s3: dict = event['Records'][0]['s3']
    bucket_name: str = s3['bucket']['name']
    object_key: str = s3['object']['key']

    return bucket_name, object_key


def get_object(bucket: str, key: str):
    s3_resource = boto3.resource('s3')
    obj_obj = s3_resource.Object(bucket, key)

    obj = obj_obj.get()
    return obj['Body'].read().decode('utf-8')


def read_json(json_str: str) -> SourceFile:
    _dict = json.loads(json_str)
    return SourceFile(_dict)


def get_prices(prices_json_path: str) -> dict:
    with open(prices_json_path, encoding='utf-8') as f:
        r = f.read()
    return json.loads(r)


def set_prices(sf: SourceFile, prices: dict) -> SourceFile:
    return sf.set_prices(prices)


def get_total_sold_price(sf: SourceFile) -> int:
    return sf.get_total_sold_price()


def get_total_buy_price(sf: SourceFile) -> int:
    return sf.get_total_buy_price()
