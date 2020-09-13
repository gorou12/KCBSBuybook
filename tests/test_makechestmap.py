import os
from buy_book import makechestmap


def test_get_messages(Snsevent):
    """メッセージのリストが返却されること."""
    assert makechestmap.get_messages(Snsevent) == \
        [Snsevent['Records'][0]['Sns']['Message']]


def test_generate_message():
    """メッセージからDiscord用テキストを生成できること."""
    url = "http://www.example.com/"
    excepted = (
        "チェストマップ：http://www.example.com/"
    )
    assert makechestmap.generate_message(url) == excepted


def test_put_to_bucket(put_s3_setup):
    os.environ['OUTPUT_BUCKET_NAME'] = "KCBSOutputBucket"
    os.environ['OUTPUT_BUCKET_ENDPOINT'] = "example.com"
    example_content = "hogehoge"
    key, _ = makechestmap.put_to_bucket("hogehoge")
    obj = put_s3_setup.Object(key).get()
    assert obj['Body'].read().decode('utf-8') == example_content
