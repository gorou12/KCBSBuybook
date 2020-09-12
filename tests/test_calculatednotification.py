from buy_book import calculatednotification


def test_get_messages(Snsevent):
    """メッセージのリストが返却されること."""
    assert calculatednotification.get_messages(Snsevent) == \
        [Snsevent['Records'][0]['Sns']['Message']]


def test_generate_message(example_created_message):
    """メッセージからDiscord用テキストを生成できること."""
    excepted = (f"計算終了しました。\r"
                f"販売点数：164\r"
                f"買取点数：81")
    assert calculatednotification.generate_message(example_created_message) ==\
        excepted
