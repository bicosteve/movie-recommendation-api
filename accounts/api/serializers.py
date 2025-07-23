from rest_framework import serializers
from django.contrib.auth.hashers import make_password


from accounts.models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    """
    RegisterSerializer is used to parse the registeration payload into pythonic data type.
    """

    confirn_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password", "confirm_password"]
        exra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        """
        This method will be called when serializer.is_valid() is called.
        It will be used to check passwords match, detect double username registration, and double email registration.
        """
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"err": "Password & confirm password do not match!"}
            )

        if CustomUser.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError({"err": "User already exists!"})

        if CustomUser.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"err": "email is already taken"})
        return data

    def create(self, validated_data):
        """
        This method will be caleed when serializer.save() is called.
        It will pop the confirm_password which is not stored in the table
        It will hash the password
        It will create a user on the CustomUser model
        """
        validated_data.pop("confirm_password")
        validated_data["password"] = make_password(validated_data["password"])
        return CustomUser.objects.create(**validated_data)
