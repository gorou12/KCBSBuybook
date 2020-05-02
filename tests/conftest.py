import boto3
import pytest
import datetime
import botostubs
from moto import mock_s3

from buy_book.SourceFile import SourceFile, Book, Enchantment


@pytest.fixture()
def sample_object():
    bucket_name = 'kcbs-buy-book-kcbsjsoninputbucket'
    object_key = '200501_180827_505.json'
    body = '{"created_date":"2020-05-01 18:42:24","books":[{"repair_times":0,"enchantments":[{"enchantment":"minecraft:flame","level":1}]},{"repair_times":0,"enchantments":[{"enchantment":"minecraft:quick_charge","level":1}]},{"repair_times":0,"enchantments":[{"enchantment":"minecraft:bane_of_arthropods","level":3},{"enchantment":"minecraft:efficiency","level":3}]}]}'
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
    s3: botostubs.S3 = boto3.resource('s3')
    bucket: botostubs.S3 = s3.create_bucket(
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
def sample_sourcefile():
    sourceFile = SourceFile(
        {
            "created_date": "2020-05-01 18:08:27",
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
