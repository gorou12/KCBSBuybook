import boto3
import pytest
from moto import mock_s3

from buy_book.SourceFile import SourceFile


@pytest.fixture()
def sample_object():
    bucket_name = 'kcbs-buy-book-kcbsjsoninputbucket'
    object_key = '200501_180827_505.json'
    body = '{"created_date": "2020-05-01 18:42:24","books": [{"repair_times": 1,"enchantments": [{"enchantment": "minecraft:protection","level": 2},{"enchantment": "minecraft:sharpness","level": 2}]},{"repair_times": 0,"enchantments": [{"enchantment": "minecraft:blast_protection","level": 2}]}]}'
    yield bucket_name, object_key, body


@pytest.fixture()
def s3event(sample_object):
    """ Generates S3 PUT Event"""
    bucket_name, object_key, body = sample_object

    yield {
        "Records": [
            {
                "eventVersion": "2.0",
                "eventSource": "aws:s3",
                "awsRegion": "ap-northeast-1",
                "eventTime": "2020-01-01T00:00:00.000Z",
                "eventName": "ObjectCreated:Put",
                "userIdentity": {
                    "principalId": "EXAMPLE"
                },
                "requestParameters": {
                    "sourceIPAddress": "127.0.0.1"
                },
                "responseElements": {
                    "x-amz-request-id": "EXAMPLE123456789",
                    "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "testConfigRule",
                    "bucket": {
                        "name": bucket_name,
                        "ownerIdentity": {
                            "principalId": "EXAMPLE"
                        },
                        "arn": "arn:aws:s3:::kcbs-buy-book-kcbsjsoninputbucket"
                    },
                    "object": {
                        "key": object_key,
                        "size": 1024,
                        "eTag": "0123456789abcdef0123456789abcdef",
                        "sequencer": "0A1B2C3D4E5F678901"
                    }
                }
            }
        ]
    }


@pytest.fixture()
def s3_setup(sample_object):
    bucket_name, object_key, body = sample_object

    mock = mock_s3()
    mock.start()
    s3 = boto3.resource('s3')
    bucket = s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            'LocationConstraint': 'ap-northeast-1'
        }
    )

    bucket.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=body
    )

    yield bucket_name, object_key, body
    mock.stop()


@pytest.fixture()
def put_s3_setup():
    mock = mock_s3()
    mock.start()
    s3 = boto3.resource('s3')

    yield s3.create_bucket(
        Bucket="KCBSOutputBucket",
        CreateBucketConfiguration={
            'LocationConstraint': 'ap-northeast-1'
        }
    )

    mock.stop()


@pytest.fixture()
def sample_sourcefile():
    sourceFile = SourceFile(
        {
            "created_date": "2020-05-01 18:42:24",
            "books": [
                {
                    "repair_times": 1,
                    "enchantments": [
                        {
                            "enchantment": "minecraft:protection",
                            "level": 2
                        },
                        {
                            "enchantment": "minecraft:sharpness",
                            "level": 2
                        }
                    ]
                },
                {
                    "repair_times": 0,
                    "enchantments": [
                        {
                            "enchantment": "minecraft:blast_protection",
                            "level": 2
                        }
                    ]
                }
            ]
        }
    )

    yield sourceFile


@pytest.fixture
def sample_prices():
    yield {
        "metadata": {
            "version": "0",
            "date": "20200101"
        },
        "prices": [
            {
                "japanese": "ダメージ軽減",
                "id": "protection",
                "price": [0, 1, 0, 0],
                "fit": ["A"]
            }, {
                "japanese": "爆発耐性",
                "id": "blast_protection",
                "price": [0, 3, 0, 0],
                "fit": ["A", "C"]
            }, {
                "japanese": "ダメージ増加",
                "id": "sharpness",
                "price": [0, 2, 0, 0, 0],
                "fit": ["B"]
            }
        ]
    }


@pytest.fixture
def source_after_price():
    yield SourceFile(
        {
            "created_date": "2020-05-01 18:42:24",
            "books": [
                {
                    "repair_times": 1,
                    "enchantments": [
                        {
                            "enchantment": "minecraft:protection",
                            "level": 2,
                            "price": 1,
                            "fit_tool": ['A']
                        },
                        {
                            "enchantment": "minecraft:sharpness",
                            "level": 2,
                            "price": 2,
                            "fit_tool": ['B']
                        }
                    ]
                },
                {
                    "repair_times": 0,
                    "enchantments": [
                        {
                            "enchantment": "minecraft:blast_protection",
                            "level": 2,
                            "price": 3,
                            "fit_tool": ['A', 'C']
                        }
                    ]
                }
            ]
        }
    )


@pytest.fixture
def example_receipt():
    yield '\r\n'.join([
        "読み取り日時：2020-05-01 18:42",
        "適用価格日付：20200101",
        "",
        "＜ 読 取 ＞",
        "合計販売点：4点",
        "合計買取点：1点",
        "※買取点は10点で1ダイヤ相当です",
        "--------内訳",
        "ダメージ軽減2, ダメージ増加2",
        "└ 合成：1回, 基礎点：1点",
        "爆発耐性2",
        "└ 合成：0回, 基礎点：3点",
        "--------以上"
    ])
