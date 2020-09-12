import boto3
import pytest
from moto import mock_s3

from buy_book.SourceFile import SourceFile


@pytest.fixture()
def sample_object():
    bucket_name = 'kcbs-buy-book-kcbsjsoninputbucket'
    object_key = '200501_180827_505.json'
    body = ('{"created_date": "2020-05-01 18:42:24",'
            '"books": [{"item_type":"enchanted_book","repair_times": 1,'
            '"enchantments": [{"enchantment": "minecraft:protection",'
            '"level": 2},{"enchantment": "minecraft:sharpness",'
            '"level": 2}]},{"item_type":"enchanted_book","repair_times": 0,'
            '"enchantments": [{"enchantment": "minecraft:blast_protection",'
            '"level": 2}]},{"item_type":"eco_egg","count":16}]}')
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
                    "x-amz-id-2": ("EXAMPLE123/5678abcdefghijklambdaisawesome"
                                   "/mnopqrstuvwxyzABCDEFGH")
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
def Snsevent(sample_object):
    """ Generates SNS Event"""

    yield {
        "Records": [
            {
                "EventVersion": "1.0",
                "EventSubscriptionArn": ("arn:aws:sns:us-east-2:123456789012:"
                                         "sns-lambda:21be56ed-a058-49f5-8c98"
                                         "-aedd2564c486"),
                "EventSource": "aws:sns",
                "Sns": {
                    "SignatureVersion": "1",
                    "Timestamp": "2019-01-02T12:45:07.000Z",
                    "Signature": ("tcc6faL2yUC6dgZdmrwh1Y4cGa/"
                                  "ebXEkAi6RibDsvpi+tE/1+82j...65r=="),
                    "SigningCertUrl": ("https://sns.us-east-2.amazonaws.com/"
                                       "SimpleNotificationService-"
                                       "ac565b8b1a6c5d002d285f9598aa1d9b.pem"),
                    "MessageId": "95df01b4-ee98-5cb9-9903-4c221d41eb5e",
                    "Message": "Hello from SNS!",
                    "MessageAttributes": {
                        "Test": {
                            "Type": "String",
                            "Value": "TestString"
                        },
                        "TestBinary": {
                            "Type": "Binary",
                            "Value": "TestBinary"
                        }
                    },
                    "Type": "Notification",
                    "UnsubscribeUrl": ("https://sns.us-east-2.amazonaws.com/"
                                       "?Action=Unsubscribe&amp;Subscription"
                                       "Arn=arn:aws:sns:us-east-2:"
                                       "123456789012:test-lambda:21be56ed-"
                                       "a058-49f5-8c98-aedd2564c486"),
                    "TopicArn": ("arn:aws:sns:us-east-2:123456789012:"
                                 "sns-lambda"),
                    "Subject": "TestInvoke"
                }
            }
        ]
    }


@pytest.fixture()
def sample_sourcefile():
    sourceFile = SourceFile(
        {
            "created_date": "2020-05-01 18:42:24",
            "books": [
                {
                    "item_type": "enchanted_book",
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
                    "item_type": "enchanted_book",
                    "repair_times": 0,
                    "enchantments": [
                        {
                            "enchantment": "minecraft:blast_protection",
                            "level": 2
                        }
                    ]
                },
                {
                    "item_type": "eco_egg",
                    "count": 16
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
            }, {
                "japanese": "魔道書「えこたまご」",
                "id": "eco_egg",
                "price": [10],
                "fit": ["ECE"]
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
                    "item_type": "enchanted_book",
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
                    "item_type": "enchanted_book",
                    "repair_times": 0,
                    "enchantments": [
                        {
                            "enchantment": "minecraft:blast_protection",
                            "level": 2,
                            "price": 3,
                            "fit_tool": ['A', 'C']
                        }
                    ]
                },
                {
                    "item_type": "eco_egg",
                    "count": 16,
                    "unit_price": 10
                }

            ]
        }
    )


@pytest.fixture
def example_created_message():
    yield {
        "created_date": "2020-05-01T18:42:24",
        "books": [
            {
                "item_type": "enchanted_book",
                "repair_times": 1,
                "enchantments": [
                    {
                        "enchantment": "minecraft:protection",
                        "level": 2,
                        "price": 1,
                        "fit_tool": ["A"],
                        "japanese": "ダメージ軽減"
                    },
                    {
                        "enchantment": "minecraft:sharpness",
                        "level": 2,
                        "price": 2,
                        "fit_tool": ["B"],
                        "japanese": "ダメージ増加"
                    }
                ],
                "total_price": 1
            },
            {
                "item_type": "enchanted_book",
                "repair_times": 0,
                "enchantments": [
                    {
                        "enchantment": "minecraft:blast_protection",
                        "level": 2,
                        "price": 3,
                        "fit_tool": ["A", "C"],
                        "japanese": "爆発耐性"
                    }
                ],
                "total_price": 3
            },
            {
                "item_type": "eco_egg",
                "count": 16,
                "unit_price": 10,
                "total_price": 160,
                "japanese": "魔道書「えこたまご」"
            }
        ],
        "price_meta": {
            "version": "0.1",
            "date": "20200101"
        },
        "total_sold_price": 164,
        "total_buy_price": 81
    }


@pytest.fixture
def example_receipt():
    yield '\r\n'.join([
        "読み取り日時：2020-05-01 18:42",
        "　　適用価格：20200101",
        "",
        "＜ 買 取 ＞",
        "合計買取点：81点",
        "※10点で1ダイヤ粒です",
        "--------内訳",
        "ダメージ軽減2, ダメージ増加2",
        "└ 合成：1回, 単価：1点",
        "爆発耐性2",
        "└ 合成：0回, 単価：3点",
        "魔道書「えこたまご」 *16",
        "└ 単価：160点",
        "--------以上"
    ])
