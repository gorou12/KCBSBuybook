import os
from buy_book import calculate


def test_get_objectinfo(s3event):
    """バケット名,キーのタプルが返却されること."""
    assert calculate.get_objectinfo(s3event) == \
        (
            s3event['Records'][0]['s3']['bucket']['name'],
            s3event['Records'][0]['s3']['object']['key']
        )


def test_get_object(s3_setup):
    bucket, key, body = s3_setup
    assert calculate.get_object(bucket, key) == body


def test_read_json(sample_object, sample_sourcefile):
    _, _, body = sample_object
    actually = calculate.read_json(body)
    assert actually == sample_sourcefile


def test_get_prices(sample_prices):
    actually = sample_prices
    assert actually ==\
        calculate.get_prices("tests/testdata/example_prices.json")


def test_set_prices(sample_sourcefile, sample_prices, source_after_price):
    sf = calculate.set_prices(sample_sourcefile, sample_prices)
    assert sf == source_after_price

    excepted_total = [2, 3, 160]
    actually_total = []
    for book in sf.books:
        total = book.get_total_price()
        actually_total.append(total)
    assert actually_total == excepted_total
    assert False


def test_get_total_sold_price(sample_sourcefile, sample_prices):
    sf = calculate.set_prices(sample_sourcefile, sample_prices)
    excepted = int(2 * 0.8 + 3 * 1.0 + 10 * 16)
    assert calculate.get_total_sold_price(sf) == excepted


def test_get_total_buy_price(sample_sourcefile, sample_prices):
    sf = calculate.set_prices(sample_sourcefile, sample_prices)
    excepted = int((2 * 0.8) * 0.5) +\
        int((3 * 1.0) * 0.5) +\
        int((10 * 16) * 0.5)
    assert calculate.get_total_buy_price(sf) == excepted


def test_create_receipt(sample_sourcefile, sample_prices, example_receipt):
    sf = calculate.set_prices(sample_sourcefile, sample_prices)
    actually, _, _ = calculate.create_receipt(sf)
    assert actually == example_receipt


def test_put_to_bucket(put_s3_setup):
    os.environ['OUTPUT_BUCKET_NAME'] = "KCBSOutputBucket"
    os.environ['OUTPUT_BUCKET_ENDPOINT'] = "example.com"
    example_content = "hogehoge"
    key, _ = calculate.put_to_bucket("hogehoge")
    obj = put_s3_setup.Object(key).get()
    assert obj['Body'].read().decode('utf-8') == example_content
