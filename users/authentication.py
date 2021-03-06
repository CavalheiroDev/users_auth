from rest_framework.authentication import BaseAuthentication
from django.http.request import HttpRequest
from rest_framework import exceptions
from django.conf import settings
import jwt

from users.models import User


class SafeJWTAuthentication(BaseAuthentication):

    def authenticate(self, request: HttpRequest):
        
        authorization_header = request.headers.get("Authorization")

        if not authorization_header:
            return None
        
        try:
            access_token = authorization_header.split(" ")[1]
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Access_token expired")
        except IndexError:
            raise exceptions.AuthenticationFailed("Token prefix missing")
        
        user = User.objects.filter(id=payload["user_id"]).first()
        if user is None:
            raise exceptions.AuthenticationFailed("User not found")

        if not user.is_active:
            raise exceptions.AuthenticationFailed("User is inactive")

        return [user, None]
