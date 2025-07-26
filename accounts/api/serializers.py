from rest_framework import serializers
import re

from accounts.models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    """
    RegisterSerializer is used to parse the registeration payload into pythonic data type.
    """

    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=1)
    confirm_password = serializers.CharField(write_only=True, min_lenght=1)

    def validate_email(self, value):
        """Used to validate that the provide email take email format"""

        disposable_mails = ["mailinator.com", "tempmail.com", "10minuteemail.com"]
        domain = value.split("@")[1]
        if domain.lower() in disposable_mails:
            raise serializers.ValidationError("Disposable mails not allowed")
        return value

    def validate_username(self, value):
        """used to validate if provided username matches a regex"""
        if not re.match(r"^[a-zA-Z0-9]+$", value):
            raise serializers.ValidationError(
                "Username can only contain numbers & letters"
            )
        return value

    def validate_passwords(data):
        """Used to validate if the provided passwords are equal and match"""
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError("Passwords must match")
        return data


class LoginSerializer(serializers.Serializer):
    """Serializes the login data"""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
