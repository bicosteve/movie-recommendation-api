from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


from accounts.services.user import UserService
from accounts.utils.logs import Logger

service = UserService()
logger = Logger()


token_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "access_tkn": openapi.Schema(
            type=openapi.TYPE_STRING, description="JWT access token"
        ),
        "refresh_tkn": openapi.Schema(
            type=openapi.TYPE_STRING, description="JWT refresh token"
        ),
    },
    example={
        "access_tkn": "your.jwt.access.token",
        "refresh_tkn": "your.jwt.refresh.token",
    },
)


class CustomTokenObatinPairView(TokenObtainPairView):
    """API view for generating access and refresh tokens"""

    @swagger_auto_schema(
        operation_description="Authenticate a user and return JWT access & refresh tokens.",
        request_body=TokenObtainPairSerializer,
        responses={
            200: token_response_schema,
            400: "Bad request",
            404: "Invalid credentials",
            500: "Server error during login",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


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
