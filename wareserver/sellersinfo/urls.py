from django.urls import path
from .views import user_inform, seller_profile, fbs_orders, send_stikers, myProfile #, my_token_obtain_pair_view, my_custom_view, addNewSeller, user_auth_view

urlpatterns = [
    # path('register/', user_registration_view, name='register'),
    # path('authpage/', user_auth_view, name='authpage'),
    # path('login/', my_token_obtain_pair_view, name='login'),
    path('info/', user_inform, name='info'),
    path('seller/<int:seller_id>/', seller_profile, name='seller_profile'),
    path('fbs_orders/<int:seller_id>/', fbs_orders, name='fbs_orders'),
    path('get_id_orders/', send_stikers, name = 'get_id_orders'),
    path('myprofile/',myProfile,name='myProfile')
    # path('addNewSeller/', addNewSeller, name='addNewSeller')
]