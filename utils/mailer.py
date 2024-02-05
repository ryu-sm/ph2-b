import boto3
from importlib import import_module
from core.config import settings


def send_email(to, template, link):
    ses = boto3.client(
        "ses",
        aws_access_key_id=settings.MAIL_ACCESS_KEY_ID,
        aws_secret_access_key=settings.MAIL_SECRET_ACCESS_KEY,
        region_name=settings.MAIL_REGION_NAME,
    )
    template_module = import_module(f"templates.{template}")

    ses.send_email(
        Source=settings.MAIL_SENDER,
        Destination={"ToAddresses": [to]},
        Message={
            "Subject": {"Data": template_module.TITLE},
            "Body": {"Html": {"Data": template_module.BODY.format(link=link)}},
        },
    )
