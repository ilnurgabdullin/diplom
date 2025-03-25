from django.urls import path
from .views import *

urlpatterns = [
    path('info/', user_inform, name='info'),
    path('seller/<int:seller_id>/', seller_profile, name='seller_profile'),
    path('fbs_orders/<int:seller_id>/', fbs_orders, name='fbs_orders'),
    path('get_id_orders/', send_stikers, name = 'get_id_orders'),
    path('myprofile/', myProfile, name='myProfile'),
    path('selection_sheet/<int:seller_id>/',selectionSheet ,name='selection_sheet'),
    path('fbs_supplies/<int:seller_id>/',fbs_supplies ,name='fbs_supplies'),
    path('my_warehouse/',my_warehouse_template ,name='my_warehouse_template'),
    path('create_warehouse/',create_warehouse ,name='create_warehouse'),
    path('get_my_storages/',get_my_storages ,name='get_my_storages'),
    path('get_cells/', get_cells, name='get_cells'),
    path('create_cell/',create_cell ,name='create_cell')
]