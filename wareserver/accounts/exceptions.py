from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import redirect

def custom_exception_handler(exc, context):
    # Вызовите стандартный обработчик исключений DRF
    response = exception_handler(exc, context)
    try:
         stc = response.status_code
    except Exception as er:
         print(er)
         return redirect('home')
    
    if stc in [401, 403] :
         return redirect('home')
    # try:
    #     if response.status_code == 403 or response.status_code == 401:
    #         return redirect('home')
    # except:
    #     return redirect('home')

    return response