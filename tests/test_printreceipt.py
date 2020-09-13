import os
from buy_book import printreceipt


def test_get_messages(Snsevent):
    """メッセージのリストが返却されること."""
    assert printreceipt.get_messages(Snsevent) == \
        [Snsevent['Records'][0]['Sns']['Message']]


def test_generate_message():
    """メッセージからDiscord用テキストを生成できること."""
    url = "http://www.example.com/"
    excepted = (
        "レシート：\n"
        "アドレスをブラウザに\n"
        "コピペしてご覧ください\n"
        "\n"
        "レシートは一定期間で\n"
        "削除します\n"
        "\n"
        "この本が不要な際は\n"
        "樽やお近くのチェストに\n"
        "お入れください\n"
        "http://www.example.com/"
    )
    assert printreceipt.generate_message(url) == excepted


def test_create_receipt(example_created_message, example_receipt):
    actually = printreceipt.generate_receipt(example_created_message)
    assert actually == example_receipt


def test_put_to_bucket(put_s3_setup):
    os.environ['OUTPUT_BUCKET_NAME'] = "KCBSOutputBucket"
    os.environ['OUTPUT_BUCKET_ENDPOINT'] = "example.com"
    example_content = "hogehoge"
    key, _ = printreceipt.put_to_bucket("hogehoge")
    obj = put_s3_setup.Object(key).get()
    assert obj['Body'].read().decode('utf-8') == example_content
