import json
import boto3
import base64
import magic
from core.config import settings


s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)


def upload_to_s3(file_name, file_content):
    s3_client.put_object(Bucket=settings.AWS_BUCKET_NAME, Key=file_name, Body=file_content)


def delete_from_s3(file_name):
    s3_client.delete_object(Bucket=settings.AWS_BUCKET_NAME, Key=file_name)


def download_from_s3(file_name):

    file_obj = s3_client.get_object(Bucket=settings.AWS_BUCKET_NAME, Key=file_name)
    file_content = file_obj["Body"].read()

    mime_type = magic.from_buffer(file_content, mime=True)

    base64_encoded_data = base64.b64encode(file_content).decode("utf-8")
    src = f"data:{mime_type};base64,{base64_encoded_data}"
    return {"name": file_name.split("/")[-1], "src": src}


def upload_buffer_to_s3(file_name, excel_buffer):
    s3_client.upload_fileobj(excel_buffer, Bucket=settings.AWS_BUCKET_NAME, Key=file_name)


def generate_presigned_url(object_key, expiration=3600):
    return s3_client.generate_presigned_url(
        "get_object", Params={"Bucket": settings.AWS_BUCKET_NAME, "Key": object_key}, ExpiresIn=expiration
    )


def upload_base64_file_s3(full_key: str, base64_file: str):
    [file_type, file_content_str] = base64_file.split(",")
    file_content = base64.b64decode(file_content_str)
    s3_client.put_object(Bucket=settings.AWS_BUCKET_NAME, Key=full_key, Body=file_content)
