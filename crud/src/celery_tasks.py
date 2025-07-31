from celery import Celery

from crud.src.config import Config
from crud.src.mail import create_message
from crud.src.mail import mail, create_message
from asgiref.sync import async_to_sync

c_app = Celery()

c_app.config_from_object('crud.src.config')

@c_app.task()
def send_email(recipients: list[str], subject: str, html_message: str) -> None:
    message = create_message(
        recipients=recipients,
        subject=subject,
        body=html_message)

    async_to_sync(mail.send_message)(message)