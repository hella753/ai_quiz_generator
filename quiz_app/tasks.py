from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage


@shared_task
def send_email(subject: str, message: str, to: list) -> None:
    """
    Send email to the user

    :param subject: Subject of the email
    :param message: Message to be sent
    :param to: Email address of the recipient
    """
    mail = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=to
    )
    mail.send(fail_silently=False)
