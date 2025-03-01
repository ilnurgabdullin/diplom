from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Получаем токен из куки
        auth = request.COOKIES.get('access_token')

        if not auth:
            raise AuthenticationFailed('Токен отсутствует')  # Выбрасываем исключение

        # Проверяем токен
        try:
            token = AccessToken(auth)
            user_id = token['user_id']  # Извлекаем ID пользователя из токена
        except Exception:
            raise AuthenticationFailed('Недействительный токен')  # Выбрасываем исключение

        # Получаем пользователя по ID
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('Пользователь не найден')  # Выбрасываем исключение

        return user, token  # Возвращаем пользователя и токен