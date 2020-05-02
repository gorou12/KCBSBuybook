from buy_book import app
import json


def test_get_objectinfo(s3event):
    """バケット名,キーのタプルが返却されること."""
    assert app.get_objectinfo(s3event) == \
        (
            s3event['Records'][0]['s3']['bucket']['name'],
            s3event['Records'][0]['s3']['object']['key']
        )


def test_get_object(s3_setup):
    client, bucket, key, body = s3_setup
    decoded = json.loads(body)
    assert app.get_object(client, bucket, key) == decoded
