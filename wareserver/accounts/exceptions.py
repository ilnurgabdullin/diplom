from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import redirect

def custom_exception_handler(exc, context):
    # Вызовите стандартный обработчик исключений DRF
    response = exception_handler(exc, context)

    # Если исключение - AuthenticationFailed, выполните перенаправление
    if isinstance(exc, AuthenticationFailed):
        return redirect('home')

    return response