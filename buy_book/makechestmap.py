import os
import time
import json
import boto3
from typing import Tuple


def lambda_handler(event, context):
    msgs = get_messages(event)
    for msg in msgs:
        html = create_chestmap(msg)
        _, url = put_to_bucket(html)

        discord_msg = generate_message(url)
        send_to_discord(discord_msg)


def get_messages(event) -> list:
    records = event['Records']
    return [r['Sns']['Message'] for r in records]


def create_chestmap(msg: str) -> str:
    html_template_top = """
<!DOCTYPE html>
<html lang="ja">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>査定結果</title>
</head>

<body>
    <style>
        table {
            border: solid 1px black;
            border-collapse: collapse;
            vertical-align: middle;
            font-size: 12px;
            table-layout: fixed;
        }
        
        td {
            border: solid 1px black;
            width: 150px;
            height: 60px;
            text-align: center;
            position: relative;
        }
        
        .solo-mix0 {
            background-color: #ffffff;
            background-image: repeating-linear-gradient(-45deg, #fff, #fff 7px, transparent 0, transparent 14px);
        }
        
        .solo-mix1 {
            background-color: #ffffdb;
            background-image: repeating-linear-gradient(-45deg, #fff, #fff 7px, transparent 0, transparent 14px);
        }
        
        .solo-mix2 {
            background-color: #ffdbed;
            background-image: repeating-linear-gradient(-45deg, #fff, #fff 7px, transparent 0, transparent 14px);
        }
        
        td .moji {
            position: absolute;
            top: 20px;
            left: 10px;
            font-size: 18px;
        }
        
        .multi-price0 {
            background-color: #f4fff4;
        }
        
        .multi-price1 {
            background-color: #ccffcc;
        }
        
        .multi-price2 {
            background-color: #a8ffa8;
        }
        
        .multi-price3 {
            background-color: #7fff7f;
        }
        
        .multi-price4 {
            background-color: #5bff5b;
        }
        
        .multi-price5 {
            background-color: #00ff00;
        }
    </style>
    <table>
    """
    html_template_bottom = """
    </table>
</body>

</html>
    """
    html_items = []

    dict_msg = json.loads(msg)
    for book in dict_msg["books"]:
        left_str = ""
        main_str = ""
        class_str = ""
        if book["item_type"] == "enchanted_book":
            enc_l = [i["japanese"] + str(i["level"])
                     for i
                     in book["enchantments"]]
            encha_cnt = len(book["enchantments"])
            repair_times = book["repair_times"]
            sold_price = book["total_price"] / 10
            if encha_cnt == 1:
                left_str = str(repair_times)
                main_str = enc_l[0]
                class_str = "solo-mix" + left_str
            else:
                left_str = str(int(sold_price))
                main_str = "<br>".join(enc_l)
                class_str = "multi-price" + left_str

        elif book["item_type"] == "eco_egg":
            sold_price = book["total_price"]
            count = book["count"]
            main_str = book["japanese"] + " *" + str(count)

        html_items.append(
            (f'<td class="{class_str}">'
             f'{main_str}'
             f'<div class="moji">{left_str}</div>'
             f'</td>'))

    html_middle = ""
    for i in range(9 * 6):
        if (i % 9 == 0):
            if (i == 0):
                html_middle += "<tr>"
            else:
                html_middle += "</tr><tr>"
        
        if len(html_items) <= i:
            html_middle += "<td></td>"
        else:
            html_middle += html_items[i - 1]

    html_middle += "</tr>"

    return html_template_top + html_middle + html_template_bottom


def put_to_bucket(content: str) -> Tuple[str, str]:
    bucket = os.environ['OUTPUT_BUCKET_NAME']
    url = os.environ['OUTPUT_BUCKET_ENDPOINT']
    key = str(int(time.time())) + ".html"

    s3_resource = boto3.resource('s3')
    obj = s3_resource.Object(bucket, key)
    obj.put(Body=content,
            ACL='public-read',
            ContentType='text/html;charset=utf-8')

    return key, f"https://{url}/{key}"


def generate_message(url: str) -> str:
    msg = (f"チェストマップ：{url}")
    return msg


def send_to_discord(msg: str):
    sns = boto3.resource('sns')
    topic = sns.Topic(os.environ['OUTPUT_SNS_ARN'])

    body = topic.publish(
        Message=msg
    )

    return body
