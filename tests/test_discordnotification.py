from buy_book import discordnotification


def test_get_messages(Snsevent):
    """メッセージのリストが返却されること."""
    assert discordnotification.get_messages(Snsevent) == \
        [Snsevent['Records'][0]['Sns']['Message']]
