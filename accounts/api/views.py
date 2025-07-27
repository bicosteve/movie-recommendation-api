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
from accounts.utils.logs import Logger

service = UserService()
logger = Logger()


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
                "verification_tkn": token,
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
            if payload.get("type") != "account_verification":
                return Response(
                    {"error": "Invalid token type"}, status=status.HTTP_400_BAD_REQUEST
                )

            email = payload.get("email")
            user_id = payload.get("user_id")

            is_verified = service.check_verified(email)

            # 1. Check if account is verified
            if is_verified == 1:
                return Response(
                    {"msg": "account is already verified"},
                    status=status.HTTP_200_OK,
                )

            # 2. Update the status of the user
            verified = service.verify(user_id)
            if verified != 1:
                return Response(
                    {"msg": "User not verified"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            if verified == 1:
                return Response(
                    {"msg": "Account successfully verified"},
                    status=status.HTTP_200_OK,
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

        # 1. Check if user exists
        is_user = service.get_by_mail(email)
        if not is_user:
            return Response(
                {"msg": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2. Check is user is verifed
        is_verified = service.check_verified(email)
        if not is_verified:
            return Response(
                {"msg": "Not verified user"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Login user

        access_tkn, refresh_tkn = service.create_session(email, password)

        if access_tkn == "":
            return Response(
                {"msg": "ACCESS_TKN:an error occured while login in"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if refresh_tkn == "":
            return Response(
                {"msg": "REFRESH_TKN:an error occured while login in"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 4. Save refresh token
        is_added = service.save_refresh_tkn(refresh_tkn)
        if not is_added:
            return Response(
                {"msg": "REFRESH_TKN: not saved!"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "access_tkn": access_tkn,
                "refresh_tkn": refresh_tkn,
            },
            status=status.HTTP_200_OK,
        )


class RefreshTokenView(APIView):
    def post(self, request):
        token = request.data.get("refresh_tkn")

        if not token:
            return Response({"err": "missing refresh token"}, status=400)

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )

            if payload.get("type") != "refresh":
                return Response({"err": jwt.InvalidTokenError()}, status=400)

            user_id = payload.get("user_id")
            email = payload.get("email")
            username = payload.get("username")

            # Generate get refresh token
            refresh_token = service.refresh_tkn(user_id)

            return Response(
                {
                    "access_tkn": access_tkn,
                    "refresh_tkn": refresh_token,
                },
                status=200,
            )

        except jwt.ExpiredSignatureError:
            return Response({"error": "Refresh token expired"}, status=403)
        except jwt.InvalidTokenError:
            return Response({"error": "Invalid refresh token"}, status=403)


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_id = user["id"]

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM refresh_tokens WHERE user_id = %s", [user_id])

        return Response({"msg": "Logged out successfully"}, status=200)
