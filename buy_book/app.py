import os
import json
import time
import boto3
import requests
import urllib.request
from datetime import datetime

from buy_book.SourceFile import SourceFile

client = boto3.client('s3')
prices_json_path = "buy_book/data/prices.json"


def lambda_handler(event, context):
    """Lambda handler."""
    bucket_name, object_key = get_objectinfo(event)
    json_str = get_object(bucket_name, object_key)
    sourceFile = read_json(json_str)
    prices = get_prices(prices_json_path)
    sourceFile = set_prices(sourceFile, prices)
    receipt, sold_p, buy_p = create_receipt(sourceFile)
    url = put_to_bucket(receipt)

    send_to_discord(sold_p, buy_p, url)

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


def create_receipt(sf: SourceFile) -> str:
    created_date = datetime.strftime(sf.created_date, "%Y-%m-%d %H:%M")
    metadata_date = sf.price_meta.get('date')
    total_sold = get_total_sold_price(sf)
    total_buy = get_total_buy_price(sf)

    receipt_l = [
        f"読み取り日時：{created_date}",
        f"適用価格日付：{metadata_date}",
        f"",
        f"＜ 読 取 ＞",
        f"合計販売点：{total_sold}点",
        f"合計買取点：{total_buy}点",
        f"※買取点は10点で1ダイヤ相当です",
        f"--------内訳",
    ]

    for book in sf.books:
        enc_l = [i.japanese + str(i.level) for i in book.enchantments]
        sold_price = book.get_sold_price()
        receipt_l.append(", ".join(enc_l))
        receipt_l.append(f"└ 基礎点：{sold_price}点")

    receipt_l.append("--------以上")

    return '\r\n'.join(receipt_l), total_sold, total_buy


def put_to_bucket(content: str) -> str:
    bucket = os.environ['OUTPUT_BUCKET_NAME']
    url = os.environ['OUTPUT_BUCKET_ENDPOINT']
    key = str(int(time.time())) + ".txt"

    s3_resource = boto3.resource('s3')
    obj = s3_resource.Object(bucket, key)
    obj.put(Body=content)

    return key, f"{url}/{key}"


def send_to_discord(sold_price: int, buy_price: int, url: str):
    endpoint = os.environ['DISCORD_ENDPOINT']
    msg = (f"計算終了しました。\r販売点数：{sold_price}\r買取点数：{buy_price}"
           f"\r詳細：{url}")
    headers = {
        "Content-Type": "application/json"
    }
    content = {
        "content": msg
    }

    body = requests.post(url=endpoint,
                         data=json.dumps(content).encode(),
                         headers=headers)

    return body
