from django.urls import path
from .views import user_registration_view, my_token_obtain_pair_view, my_custom_view, addNewSeller, user_auth_view, newFile

urlpatterns = [
    path('register/', user_registration_view, name='register'),
    path('authpage/', user_auth_view, name='authpage'),
    path('login/', my_token_obtain_pair_view, name='login'),
    path('info/', my_custom_view, name='info'),
    path('addNewSeller/', addNewSeller, name='addNewSeller'),
    path('newFile/', newFile, name='newFile')
]