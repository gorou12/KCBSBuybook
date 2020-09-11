import os
import json
import requests


def lambda_handler(event, context):
    msgs = get_messages(event)
    send_to_discord(msgs)


def get_messages(event) -> list:
    records = event['Records']
    return [r['Sns']['Message'] for r in records]


def send_to_discord(msgs: list):
    for msg in msgs:
        endpoint = os.environ['DISCORD_ENDPOINT']
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
