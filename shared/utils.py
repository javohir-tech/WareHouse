import re
import threading
from users.models import AuthType
from rest_framework.validators import ValidationError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

email_regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}"
phone_regex = r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$"


def check_auth_type(email_or_number):

    if re.fullmatch(email_regex, email_or_number):
        return AuthType.VIA_EMAIL
    elif re.fullmatch(phone_regex, email_or_number):
        return AuthType.VIA_PHONE
    else:
        raise ValidationError("siz kiritgan telefon raqam yoki email hato !!!")


class EmailThread(threading.Thread):

    def __init__(self, email):
        super().__init__()
        self.email = email

    def run(self):
        return self.email.send()


class Email:
    @staticmethod
    def send_email(data):

        email = EmailMessage(
            subject=data["subject"], body=data["body"], to=[data["email_to"]]
        )

        if data["content_type"] == "html":
            email.content_subtype = "html"

        EmailThread(email).start()


def send_email(to_email, code):
    html_content = render_to_string("user/email/send_email.html", {"code": code})

    data = {
        "subject": "Hush kelipsiz",
        "body": html_content,
        "content_type": "html",
        "email_to": to_email,
    }

    Email.send_email(data)
