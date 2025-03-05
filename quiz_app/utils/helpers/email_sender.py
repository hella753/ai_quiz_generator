from django.conf import settings
from django.core.mail import EmailMessage


class EmailSender:
    """
    This class is used to send email to the user
    """
    def __init__(self, subject, message, to):
        self.message = message
        self.to = to
        self.subject = subject
        self.from_email = settings.EMAIL_HOST_USER

    def send_email(self):
        mail = EmailMessage(
            self.subject,
            body=self.message,
            from_email=self.from_email,
            to=self.to
        )
        mail.send(fail_silently=False)
