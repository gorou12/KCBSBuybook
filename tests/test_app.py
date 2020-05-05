from buy_book import app, SourceFile
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
    actually = app.read_json(body)
    assert actually == sample_sourcefile


def test_get_prices(sample_prices):
    actually = sample_prices
    assert actually == app.get_prices("tests/testdata/example_prices.json")


def test_set_prices(sample_sourcefile, sample_prices, source_after_price):
    sf = app.set_prices(sample_sourcefile, sample_prices)
    assert sf == source_after_price

    excepted_total = [2, 3]
    actually_total = []
    for book in sf.books:
        total = book.get_total_price()
        actually_total.append(total)
    assert actually_total == excepted_total


def test_get_total_sold_price(sample_sourcefile, sample_prices):
    sf = app.set_prices(sample_sourcefile, sample_prices)
    excepted = int(2 * 0.8 + 3 * 1.0)
    assert app.get_total_sold_price(sf) == excepted


def test_get_total_buy_price(sample_sourcefile, sample_prices):
    sf = app.set_prices(sample_sourcefile, sample_prices)
    excepted = int((2 * 0.8 + 3 * 1.0) * 0.5)
    assert app.get_total_buy_price(sf) == excepted
