from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from .serializers import RegisterSerializer


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        """Used to validate the incoming data"""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "user registered. verify your account"},
                status=status.HTTP_201_CREATED,
            )
        return Response({"msg": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
