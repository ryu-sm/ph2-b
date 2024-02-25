import json
import boto3
import base64
import magic


AWS_ACCESS_KEY_ID = "AKIAZI2LIM6U7DG4IEE7"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION = "ap-northeast-1"
BUCKET_NAME = "dev-p-files"

s3_client = boto3.client(
    "s3", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION
)


def upload_to_s3(file_name, file_content):
    s3_client.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=file_content)


def download_from_s3(file_name):

    file_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_name)
    file_content = file_obj["Body"].read()

    mime_type = magic.from_buffer(file_content, mime=True)

    base64_encoded_data = base64.b64encode(file_content).decode("utf-8")
    src = f"data:{mime_type};base64,{base64_encoded_data}"
    return {"name": file_name.split("/")[-1], "src": src}
