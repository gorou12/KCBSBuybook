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


def test_get_dict(sample_sourcefile, sample_prices):
    sf = calculate.set_prices(sample_sourcefile, sample_prices)
    excepted_sold = int(2 * 0.8 + 3 * 1.0 + 10 * 16)
    excepted_buy = int((2 * 0.8) * 0.5) +\
        int((3 * 1.0) * 0.5) +\
        int((10 * 16) * 0.5)
    actually = calculate.get_dict(sf)
    assert actually["total_sold_price"] == excepted_sold
    assert actually["total_buy_price"] == excepted_buy
