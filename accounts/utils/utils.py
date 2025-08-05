from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime, timedelta
import jwt


class Utils:
    @staticmethod
    def generate_verification_token(user_id, email, username) -> str:
        payload = {
            "user_id": user_id,
            "email": email,
            "username": username,
            "exp": datetime.now() + timedelta(hours=6),
            "type": "account_verification",
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return token

    @staticmethod
    def generate_tokens(user_id, email):
        access_payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.now() + timedelta(minutes=50),
            "type": "access_token",
        }

        refresh_payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.now() + timedelta(days=7),
            "type": "refresh_token",
        }

        access_token = jwt.encode(
            access_payload, settings.SECRET_KEY, algorithm="HS256"
        )

        refresh_token = jwt.encode(
            refresh_payload, settings.SECRET_KEY, algorithm="HS256"
        )

        return access_token, refresh_token

    @staticmethod
    def send_verification_mail(email, username, token) -> int:
        verify_url = f"http://localhost:8000/user/verify-account/?token={token}"
        subject = "Account verification mail"
        msg = f"Hello, {username}, \n click this link {verify_url} to verify your account."

        is_success = send_mail(
            subject=subject,
            message=msg,
            from_email="no-reply@test.com",
            recipient_list=[
                email,
            ],
            fail_silently=False,
        )

        return is_success
