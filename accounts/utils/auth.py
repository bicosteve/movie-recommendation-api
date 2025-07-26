from django.conf import settings
from django.db import connection


from rest_framework import authentication, exceptions
import jwt


class JWTAuthentication(authentication.BaseAuthentication):
    pass
