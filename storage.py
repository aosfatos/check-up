import boto3
from decouple import config


def get_client():
    try:
        client = boto3.client(
            "s3",
            aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
            region_name=config("AWS_S3_REGION_NAME"),
        )
    except AttributeError:
        raise Exception("Credentials not found")
    return client


def upload_file(file_path, object_name):
    s3_client = get_client()
    bucket = config("AWS_BUCKET_NAME")
    response = s3_client.upload_file(file_path, bucket, f"screenshots/{object_name}")

    return f"s3://{bucket}/{object_name}"
