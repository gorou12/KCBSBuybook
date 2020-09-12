import os
import boto3


def lambda_handler(event, context):
    msgs = get_messages(event)
    for json_msg in msgs:
        msg = generate_message(json_msg)
        send_to_discord(msg)


def get_messages(event) -> list:
    records = event['Records']
    return [r['Sns']['Message'] for r in records]


def generate_message(json_msg: str) -> str:
    return json_msg


def send_to_discord(msg: str):
    sns = boto3.resource('sns')
    topic = sns.Topic(os.environ['OUTPUT_SNS_ARN'])

    body = topic.publish(
        Message=msg
    )

    return body
