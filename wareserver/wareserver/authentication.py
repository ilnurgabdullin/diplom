from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        auth = request.COOKIES.get('access_token')

        if not auth:
            login_url = '/' 
            raise PermissionDenied(login_url) 
        try:
            token = AccessToken(auth)
            user_id = token['user_id']
        except Exception:
            raise AuthenticationFailed('Недействительный токен')

        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('Пользователь не найден')

        return user, token




