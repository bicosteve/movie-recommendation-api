from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken


from accounts.utils.logs import Logger
from .schemas import token_response_schema, logout_response_schema


logger = Logger()


class CustomObtainPairView(TokenObtainPairView):
    """
    Handles user authentication by validating credentials and issuing JWT tokens.

    This view extends SimpleJWT's `TokenObtainPairView` to provide an API endpoint
    for logging in users. Upon successful authentication, it returns both an
    access token and a refresh token in JSON format.

    Key points:
    - Allows any user (authenticated or not) to attempt login (`AllowAny`).
    - Uses `TokenObtainPairSerializer` to validate credentials.
    - Returns HTTP 200 with tokens if login is successful.
    - Returns HTTP 400 if the request is invalid or the user is not verified.
    - Returns HTTP 404 if the user does not exist.
    - Returns HTTP 500 if an unexpected server error occurs.
    - Swagger documentation is extended via `@extend_schema` for clear API docs.
    """

    permission_classes = (AllowAny,)

    @extend_schema(
        operation_id="user_login",
        description="Authenticate a user and return JWT access & refresh tokens.",
        request=TokenObtainPairSerializer,
        responses={
            200: OpenApiResponse(
                response=token_response_schema,
                description="Tokens returned successfully",
            ),
            400: OpenApiResponse(description="User not verified or bad request"),
            404: OpenApiResponse(description="User not found"),
            500: OpenApiResponse(description="Server error during login"),
        },
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    """
    API endpoint for securely logging out a user by blacklisting their JWT refresh token.

    Authentication:
    - Requires a valid JWT access token in the `Authorization` header.
    - Uses `JWTAuthentication` to identify the authenticated user.
    - Only authenticated users (`IsAuthenticated`) can access this endpoint.

    Behavior:
    - Accepts a POST request containing the user's refresh token in the request body.
    - Validates that a `refresh` field is provided.
    - Uses SimpleJWT's `RefreshToken` to blacklist the provided refresh token.
    - Once blacklisted, the refresh token can no longer be used to obtain new access tokens.
    - The current access token remains valid until it expires naturally (unless you also blacklist it manually).

    Request Body (JSON):
    {
        "refresh": "<refresh_token>"
    }

    Responses:
    - 200 OK: Logout successful, refresh token blacklisted.
      Example: {"msg": "Logged out successfully"}
    - 400 Bad Request: Missing or invalid refresh token.
      Example: {"error": "Refresh token required"}
    - 401 Unauthorized: No valid access token provided in Authorization header.
    - 500 Internal Server Error: Unexpected failure during token blacklisting.

    Security Notes:
    - This endpoint ensures that refresh tokens cannot be reused after logout.
    - Access tokens remain valid until expiry unless you implement an access token blacklist.
    - Best practice is to keep short access token lifetimes and rely on refresh token blacklisting for security.

    OpenAPI/Swagger:
    - Uses `@extend_schema` for documented operation, responses, and example payloads.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="user_logout",
        description="Log out the authenticated user by invalidating their token/session.",
        responses={
            200: logout_response_schema,
            400: logout_response_schema,
        },
    )
    def post(self, request):
        user = request.user

        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token required"}, status=400)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"msg": "Logged out successfully"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
