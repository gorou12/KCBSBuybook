def lambda_handler(event, context):
    """Lambda handler."""
    print(event)
    bucket_name, object_key = get_objectinfo(event)
    return


def get_objectinfo(event: dict):
    """S3イベントからバケット名とオブジェクトキーを取り出す.

    Arguments:
        event {dict} -- S3イベント.

    Returns:
        tuple(str, str) -- バケット名, オブジェクトキー
    """
    s3: dict = event['Records'][0]['s3']
    bucket_name: str = s3['bucket']['name']
    object_key: str = s3['object']['key']

    return bucket_name, object_key
