import os
import time
import json
import boto3
from datetime import datetime
from typing import Tuple


def lambda_handler(event, context):
    msgs = get_messages(event)
    for msg in msgs:
        receipt = generate_receipt(msg)
        _, url = put_to_bucket(receipt)

        discord_msg = generate_message(url)
        send_to_discord(discord_msg)


def get_messages(event) -> list:
    records = event['Records']
    return [r['Sns']['Message'] for r in records]


def generate_receipt(msg: str) -> str:
    dict_msg = json.loads(msg)
    created_date = datetime.fromisoformat(dict_msg["created_date"])
    created_date = created_date.strftime("%Y-%m-%d %H:%M")
    metadata_date = dict_msg["price_meta"]["date"]
    total_buy = dict_msg["total_buy_price"]

    receipt_l = [
        f"読み取り日時：{created_date}",
        f"　　適用価格：{metadata_date}",
        f"",
        f"KamaCoop BookStoreをご利用いただき",
        f"ありがとうございます。",
        f"計算結果をお知らせします。",
        f"",
        f"＜ 買 取 ＞",
        f"合計買取点：{total_buy}点",
        f"",
        f"※内訳の「単価」の約半額が",
        f"　合計買取点です",
        f"",
        f"※10点＝1ダイヤ粒です",
        f"",
        f"--------内訳",
    ]

    item_count = 0
    for book in dict_msg["books"]:
        if book["item_type"] == "enchanted_book":
            enc_l = [i["japanese"] + str(i["level"])
                     for i
                     in book["enchantments"]]
            sold_price = book["total_price"]
            repair_times = book["repair_times"]
            receipt_l.append(", ".join(enc_l))
            receipt_l.append(f"└ 合成：{repair_times}回, 単価：{sold_price}点")
            item_count += 1
        elif book["item_type"] == "eco_egg":
            sold_price = book["total_price"]
            count = book["count"]
            receipt_l.append(book["japanese"] + " *" + str(count))
            receipt_l.append(f"└ 単価：{sold_price}点")
            item_count += 1

    receipt_l.append(f"--------以上")
    receipt_l.append(f"")
    receipt_l.append(f"計算対象：{item_count}スロット")

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
    msg = (f"レシート：\n"
           f"アドレスをブラウザに\n"
           f"コピペしてご覧ください\n"
           f"\n"
           f"レシートは一定期間で\n"
           f"削除します\n"
           f"\n"
           f"この本が不要な際は\n"
           f"樽やお近くのチェストに\n"
           f"お入れください\n"
           f"{url}")
    return msg


def send_to_discord(msg: str):
    sns = boto3.resource('sns')
    topic = sns.Topic(os.environ['OUTPUT_SNS_ARN'])

    body = topic.publish(
        Message=msg
    )

    return body
