from buy_book import app


def test_get_objectinfo(s3event):
    """バケット名,キーのタプルが返却されること."""
    assert app.get_objectinfo(s3event) == \
        (
            s3event['Records'][0]['s3']['bucket']['name'],
            s3event['Records'][0]['s3']['object']['key']
        )
