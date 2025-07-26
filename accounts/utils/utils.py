from django.conf import settings
from django.core.mail import send_mail

import jwt
from datetime import datetime, timedelta


class Utils:
    def __init__(self, user):
        self.user = user

    def generate_verification_token(self) -> str:
        payload = {
            "user_id": self.user.id,
            "email": self.user.email,
            "username": self.user.username,
            "exp": datetime.datetime.now() + timedelta(hours=24),
            "type": "email_verification",
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return token

    def send_verification_mail(self, token) -> int:
        verify_url = f"http://localhost:8000/user/verify-email/?token={token}"
        subject = "Account verification mail"
        msg = f"Hello, {self.user.username}, \n click this link {verify_url} to verify your account."

        is_success = send_mail(
            subject=subject,
            message=msg,
            from_email="no-reply@test.com",
            recipient_list=[
                self.user.email,
            ],
            fail_silently=False,
        )

        return is_success

    def generate_jwt_token(self, user_id, email) -> str:
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.datetime.now() + timedelta(hours=5),
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        return token
