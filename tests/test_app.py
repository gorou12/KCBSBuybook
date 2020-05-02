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
    bucket, key, body = s3_setup
    assert app.get_object(bucket, key) == body


def test_read_json(sample_object, sample_sourcefile):
    _, _, body = sample_object
    assert app.read_json(body) == sample_sourcefile
