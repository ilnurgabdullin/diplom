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
    path('goods/', goods_template, name='goods'),
    path('add_good/', add_good, name='add_good'),
    path('get_goods/', get_goods, name='get_goods'),
    path('get_podbor_list/', get_podbor_list, name='get_podbor_list'),
    path('add_product_to_cell/', add_product_to_cell, name='add_product_to_cell'),
    path('create_cell/',create_cell ,name='create_cell'),
    path('stikers/<path:sticker_id>/', get_stikers, name='stickers'),
    path('supplies/<path:sticker_id>/', get_supplies, name='stickers'),
    path('update_good/', update_good, name='update_good'),
    path('chek_token/', chek_token, name='chek_token'),
    path('editSettings/', editSettings, name='editSettings'),
    path('delete/<int:cell_id>/', delete_storage_cell, name='delete_storage_cell')
]


