from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt, datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import RegisterSerializer, LoginSerializer
from accounts.utils.utils import Utils
from accounts.services.user import UserService
from accounts.utils.logs import Logger

service = UserService()
logger = Logger()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"data": serializer.data}, status=201)


class LoginView(APIView):
    """API view for login"""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        payload = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "exp": datetime.datetime.utcnow() + settings.JWT_EXP_DELTA,
        }

        token = jwt.encode(
            payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )

        return Response(
            {
                "token": token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            }
        )


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not hasattr(user, "id"):
            return Response({"error": "Invalid user"}, status=400)

        user_id = user.id
        service.logout(user_id)

        return Response({"msg": "Logged out successfully"}, status=200)
