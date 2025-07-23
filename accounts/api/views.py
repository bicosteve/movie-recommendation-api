from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt


from .serializers import RegisterSerializer
from accounts.models import CustomUser
from accounts.utils.utils import Utils


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        """Used to validate the incoming data"""

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            utils = Utils(user)
            token = utils.generate_verification_token()
            utils.send_verification_mail(token)
            return Response(
                {"msg": "user registered. verify your account"},
                status=status.HTTP_201_CREATED,
            )
        return Response({"msg": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            if payload.get("type") != "email_verification":
                return Response(
                    {"error": "Invalid token type"}, status=status.HTTP_400_BAD_REQUEST
                )

            user_id = payload["user_id"]
            user = CustomUser.objects.get(id=user_id)
            if user.is_verified:
                return Response(
                    {"msg": "account is already verified"}, status=status.HTTP_200_OK
                )
            user.is_verified = True
            user.save()
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
