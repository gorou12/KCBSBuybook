import os
import time
import boto3
from datetime import datetime
from typing import Tuple


def lambda_handler(event, context):
    msgs = get_messages(event)
    for dict_msg in msgs:
        receipt = generate_receipt(dict_msg)
        _, url = put_to_bucket(receipt)

        msg = generate_message(url)
        send_to_discord(msg)


def get_messages(event) -> list:
    records = event['Records']
    return [r['Sns']['Message'] for r in records]


def generate_receipt(dict_msg: dict) -> str:
    created_date = datetime.fromisoformat(dict_msg["created_date"])
    created_date = created_date.strftime("%Y-%m-%d %H:%M")
    metadata_date = dict_msg["price_meta"]["date"]
    total_buy = dict_msg["total_buy_price"]

    receipt_l = [
        f"読み取り日時：{created_date}",
        f"　　適用価格：{metadata_date}",
        f"",
        f"＜ 買 取 ＞",
        f"合計買取点：{total_buy}点",
        f"※10点で1ダイヤ粒です",
        f"--------内訳",
    ]

    for book in dict_msg["books"]:
        if book["item_type"] == "enchanted_book":
            enc_l = [i["japanese"] + str(i["level"])
                     for i
                     in book["enchantments"]]
            sold_price = book["total_price"]
            repair_times = book["repair_times"]
            receipt_l.append(", ".join(enc_l))
            receipt_l.append(f"└ 合成：{repair_times}回, 単価：{sold_price}点")
        elif book["item_type"] == "eco_egg":
            sold_price = book["total_price"]
            count = book["count"]
            receipt_l.append(book["japanese"] + " *" + str(count))
            receipt_l.append(f"└ 単価：{sold_price}点")

    receipt_l.append("--------以上")

    return '\r\n'.join(receipt_l)


def put_to_bucket(content: str) -> Tuple[str, str]:
    bucket = os.environ['OUTPUT_BUCKET_NAME']
    url = os.environ['OUTPUT_BUCKET_ENDPOINT']
    key = str(int(time.time())) + ".txt"

    s3_resource = boto3.resource('s3')
    obj = s3_resource.Object(bucket, key)
    obj.put(Body=content,
            ACL='public-read',
            ContentType='text/plain;charset=utf-8')

    return key, f"https://{url}/{key}"


def generate_message(url: str) -> str:
    msg = (f"レシート：{url}")
    return msg


def send_to_discord(msg: str):
    sns = boto3.resource('sns')
    topic = sns.Topic(os.environ['OUTPUT_SNS_ARN'])

    body = topic.publish(
        Message=msg
    )

    return body
