from django.shortcuts import render
from django.db import connection, IntegrityError
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import jwt


from .serializers import RegisterSerializer, LoginSerializer
from accounts.models import CustomUser
from accounts.utils.utils import Utils
from accounts.utils.auth import JWTAuthentication
from accounts.services.user import UserService


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        """Used to validate the incoming data"""

        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"msg": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data["email"]
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        service = UserService()

        is_registered = service.get_by_mail(email)

        if is_registered:
            return Response(
                {"errr": "Email already taken"}, status=status.HTTP_400_BAD_REQUEST
            )

        is_available = service.get_by_username(username)
        if is_available:
            return Response(
                {"errr": "Username already taken"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = service.register_user(username, email, password)
        if user_id < 1:
            return Response(
                {"msg": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        user = {}
        user["user_id"] = user_id
        user["username"] = username
        user["email"] = email

        utils = Utils(user)

        token = utils.generate_verification_token()

        # token_sent = utils.send_verification_mail(token)

        return Response(
            {
                "msg": "Registeration success",
                "tkn": token,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response(
                {"err": "verification token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            if payload.get("type") != "email_verification":
                return Response(
                    {"error": "Invalid token type"}, status=status.HTTP_400_BAD_REQUEST
                )

            user_id = payload.get("user_id")

            with connection.cursor() as cursor:
                cursor.execute("SELECT is_verified FROM users WHERE id = %s", [user_id])

                user = cursor.fetchone()

                if not user:
                    return Response(
                        {"err": "User not found"}, status=status.HTTP_404_NOT_FOUND
                    )

                if user.is_verified:
                    return Response(
                        {"msg": "account is already verified"},
                        status=status.HTTP_200_OK,
                    )
                if user[0]:
                    return Response(
                        {"msg": "User already verified"}, status=status.HTTP_200_OK
                    )

                # Update the status of the user
                cursor.execute(
                    "UPDATE users SET is_verified = TRUE WHERE id = %s", [user_id]
                )

                return Response(
                    {"msg": "Account successfully verified"}, status=status.HTTP_200_OK
                )
        except jwt.ExpiredSignatureError:
            return Response(
                {"msg": "Verification link expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.DecodeError:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )
        except CustomUser.DoesNotExist:
            return Response({"err": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class LoginView(APIView):
    """API view for login"""

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        with connection.cursor() as cursor:
            q = """
            SELECT id,username,email,is_verified,hashed_password 
            FROM users WHERE email = %s
            """
            cursor.execute(q, [email])
            user = cursor.fetchone()

            if not user:
                return Response(
                    {"msg": "User not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            id, username, email, is_verified, hashed_password = user

            if not check_password(password, hashed_password):
                return Response(
                    {"err": "Invalid password or email"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not is_verified:
                return Response(
                    {"err": "Not a verified user"}, status=status.HTTP_400_BAD_REQUEST
                )

            utils = Utils(user)

            access_tkn, refresh_tkn = utils.generate_tokens(id, email)

        return Response({"token": access_tkn}, status=status.HTTP_200_OK)


class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")

        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            if payload.get("type") != "refresh":
                raise jwt.InvalidTokenError()
        except jwt.ExpiredSignatureError:
            return Response({"error": "Refresh token expired"}, status=403)
        except jwt.InvalidTokenError:
            return Response({"error": "Invalid refresh token"}, status=403)

        user_id = payload.get("user_id")
        email = payload.get("email")

        # Check the token exists on refresh_token table

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT token FROM refresh_tokens WHERE user_id = %s", [user_id]
            )
            result = cursor.fetchone()

            if not result or result[0] != refresh_token:
                return Response({"error": "Invalid refresh token"}, status=403)

        new_access_token, _ = Utils.generate_tokens(user_id, email)

        return Response({"access": new_access_token})


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_id = user["id"]

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM refresh_tokens WHERE user_id = %s", [user_id])

        return Response({"msg": "Logged out successfully"}, status=200)
