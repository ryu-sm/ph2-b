import boto3
from importlib import import_module
from core.config import settings


def send_email(to, template, link):
    ses = boto3.client("ses", region_name="ap-northeast-1")
    template_module = import_module(f"templates.{template}")

    ses.send_email(
        Source=settings.AWS_MAIL_SENDER,
        Destination={"ToAddresses": [to]},
        Message={
            "Subject": {"Data": template_module.TITLE},
            "Body": {"Text": {"Data": template_module.BODY.format(link=link)}},
        },
    )


def send_emails(to, template, link):
    ses = boto3.client("ses", region_name="ap-northeast-1")
    template_module = import_module(f"templates.{template}")

    ses.send_email(
        Source=settings.AWS_MAIL_SENDER,
        Destination={"ToAddresses": to},
        Message={
            "Subject": {"Data": template_module.TITLE},
            "Body": {"Html": {"Data": template_module.BODY.format(link=link)}},
        },
    )
