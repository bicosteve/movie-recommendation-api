from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import LoginSerializer
from accounts.services.user import UserService
from accounts.utils.logs import Logger

service = UserService()
logger = Logger()


class LoginView(APIView):
    """API view for login"""

    @swagger_auto_schema(
        operation_description="Authenticate a user and return JWT access and refresh tokens.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "access_tkn": "your.jwt.access.token",
                        "refresh_tkn": "your.jwt.refresh.token",
                    }
                },
            ),
            400: openapi.Response(description="User not verified or bad request"),
            404: openapi.Response(description="User not found"),
            500: openapi.Response(description="Server error during login"),
        },
    )
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


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logs out the authenticated user by invalidating the refresh token.",
        responses={
            200: openapi.Response(
                description="Logout successful",
                examples={"application/json": {"msg": "Logged out successfully"}},
            ),
            401: openapi.Response(
                description="Authentication credentials were not provided or invalid"
            ),
        },
        security=[{"Bearer": []}],
    )
    def post(self, request):
        user = request.user
        user_id = user["id"]

        service.logout(user_id)

        return Response({"msg": "Logged out successfully"}, status=200)
