from rest_framework import serializers
import re
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user_model
import jwt

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """
    RegisterSerializer is used to parse the registeration payload into pythonic data type.
    """

    confirm_password = serializers.CharField(
        style={"input_type", "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirm_password"]
        extra_kwargs = {"password": {"write_only": True}}

    def save(self, data):
        password = self.validated_data["password"]
        confirm_password = self.validated_data["confirm_password"]

        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        if User.objects.filter(username=self.validated_data["username"]).exists():
            raise serializers.ValidationError(
                {"error": "User with that username already exists"}
            )
        if User.objects.filter(email=self.validated_data["email"]).exists():
            raise serializers.ValidationError({"error": "User with that email exists"})

        account = User(
            email=self.validated_data["email"], username=self.validated_data["username"]
        )
        account.set_password(password)
        account.save()
        return account

    # def create(self, validated_data):
    #     validated_data.pop("confirm_password")
    #     user = User.objects.create(**validated_data)
    #     return user


class LoginSerializer(serializers.Serializer):
    """Serializes the login data"""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])

        if not user:
            raise serializers.ValidationError("Invalid credentials")
        data["user"] = user
        return data


class RefreshSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, data):
        try:
            payload = jwt.decode(
                data["token"],
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError("Token expired")
        except jwt.InvalidTokenError:
            raise serializers.ValidationError("Invalid token")

        user_id = payload.get("user_id")
        username = payload.get("username")
        email = payload.get("email")

        if not all([user_id, username, email]):
            raise serializers.ValidationError("Missing token claims")

        try:
            user = User.objects.get(id=user_id, username=username, email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")

        data["user"] = user

        return data
