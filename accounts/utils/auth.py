from django.conf import settings
from django.db import connection


from rest_framework import authentication, exceptions
import jwt


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")

        user_id = payload.get("user_id")
        email = payload.get("email")
        username = payload.get("username")

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s AND email = %s", [user_id, email]
            )

            user = cursor.fetchone()

            if not user:
                raise exceptions.AuthenticationFailed("user not found")

            return (
                {
                    "user_id": user_id,
                    "email": email,
                    "username": username,
                },
                None,
            )
