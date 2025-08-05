from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
import jwt

from accounts.services.user import UserService

user_service = UserService()


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")

        user_id = payload.get("user_id")
        email = payload.get("email")

        print({"user_id": user_id, "email": email})

        User = get_user_model()

        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("User not found")

        # user = user_service.get_user(user_id, email)

        if not user:
            raise exceptions.AuthenticationFailed("User not found")

        return (user, None)
