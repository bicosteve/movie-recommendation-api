from drf_spectacular.utils import inline_serializer
from rest_framework import serializers

token_response_schema = inline_serializer(
    name="LoginResponse",
    fields={
        "msg": serializers.CharField(help_text="Login success"),
        "access": serializers.CharField(help_text="JWT access token"),
        "refresh": serializers.CharField(help_text="JWT refresh token"),
    },
)


logout_response_schema = inline_serializer(
    name="LoginResponse",
    fields={
        "msg": serializers.CharField(help_text="Logout success"),
    },
)
