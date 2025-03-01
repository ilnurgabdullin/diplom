from rest_framework.permissions import AllowAny
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes

@api_view(['GET'])
@permission_classes([AllowAny])  # Разрешаем доступ всем пользователям
def index(request):
    return render(request, 'auth.html')  # Отдаём HTML-шаблон
