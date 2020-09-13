import os
import json
import boto3


def lambda_handler(event, context):
    msgs = get_messages(event)
    for msg in msgs:
        discord_msg = generate_message(msg)
        send_to_discord(discord_msg)


def get_messages(event) -> list:
    records = event['Records']
    return [r['Sns']['Message'] for r in records]


def generate_message(msg: str) -> str:
    dict_msg = json.loads(msg)
    msg = (f"計算終了しました。\r"
           f"販売点数：{str(dict_msg['total_sold_price'])}\r"
           f"買取点数：{str(dict_msg['total_buy_price'])}")
    return msg


def send_to_discord(msg: str):
    sns = boto3.resource('sns')
    topic = sns.Topic(os.environ['OUTPUT_SNS_ARN'])

    body = topic.publish(
        Message=msg
    )

    return body
