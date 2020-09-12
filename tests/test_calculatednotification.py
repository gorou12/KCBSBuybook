from buy_book import calculatednotification


def test_get_messages(Snsevent):
    """メッセージのリストが返却されること."""
    assert calculatednotification.get_messages(Snsevent) == \
        [Snsevent['Records'][0]['Sns']['Message']]
