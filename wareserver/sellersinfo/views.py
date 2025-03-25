# from rest_framework import generics, permissions
from rest_framework.response import Response
# from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import HttpResponse, FileResponse
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated # type: ignore
from rest_framework.response import Response
from sellersinfo.models import Sellers, Cards, InfoModel, Warehouse, Storage, StorageCell, ProductPlacement
from accounts.models import CustomUser
# from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
# from rest_framework import status
from datetime import timedelta
# from django.conf import settings
from django.shortcuts import render
from wareserver.authentication import CookieJWTAuthentication
from rest_framework.decorators import api_view, authentication_classes
from accounts.baseapi import getSimple, getStiker, getFBSorders, createPostavks, addOrderInPostavk, getPSTStiker, addPst2Del, getUserInfo, get_supply_orders, getPstInfo
from accounts.barcodes import create
# from .models import Sellers
from datetime import date
from time import sleep
import logging
logger = logging.getLogger(__name__)
from django.http import JsonResponse



@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def get_cells(request):
    try:
        warehouse_id = request.GET.get('wrh')
        if not warehouse_id:
            return JsonResponse({'error': 'Не указан ID склада'}, status=400)
        
        cells = StorageCell.objects.filter(warehouse_id=warehouse_id).prefetch_related(
            'placements__product'
        )
        
        cells_data = []
        for cell in cells:
            products = []
            for placement in cell.placements.all():
                products.append({
                    'id': placement.product.id,
                    'name': placement.product.name,
                    'quantity': placement.quantity,
                    'article': placement.product.article
                })
            
            cells_data.append({
                'id': cell.id,
                'cell_code': cell.cell_code,
                'description': cell.description,
                'products': products
            })
        print(cells_data)
        return JsonResponse({'cells': cells_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@authentication_classes([CookieJWTAuthentication])
def user_inform(request):
    return render(request, 'mainProfile.html')


@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def my_warehouse_template(request):
    return render(request, 'my_warehouse.html')


@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
# @permission_classes([IsAuthenticated])
def myProfile(request):
    # Твоя логика здесь
    return render(request, 'userProfile.html')


@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def seller_profile(request, seller_id):
    return render(request, 'profile.html', {'seller_id': seller_id})


@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def selectionSheet(request, seller_id):
    return render(request, 'selection_sheet.html', {'seller_id': seller_id})


@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def fbs_supplies(request, seller_id):
    sellers = Sellers.objects.get(id=seller_id)
    ors = reversed(getPstInfo(sellers.api_token))
    sls = [{'id':i['id'], 'name':i['name'], 'date':i['createdAt']} for i in ors]
    nam = getUserInfo(sellers.api_token)['name']
    return Response({'supplies': sls, 'selname':nam}, status=200)


@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def get_my_storages(request):
    storages = Storage.objects.filter(owner=request.user.id)
    print(storages)
    sts = [{'id':i.id, 'name':i.name} for i in storages]
    print(sts)
    return Response({'storages': sts}, status=200)





@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def fbs_orders(request, seller_id):
    # user = request.user  # Получаем данные о пользователе
    # user = CustomUser.objects.get(id=user.id)
    sellers = Sellers.objects.get(id=seller_id) # Получаем всех связанных продавцов
    # print(Warehouse.objects.get())

    ors = getFBSorders(sellers.api_token)['orders'] #,'https://marketplace-api.wildberries.ru/api/v3/orders/new')['orders']
    sls = [{'id':i['id'], 'name':Warehouse.objects.get(location_id=i['warehouseId']).name, 'skus':i['skus']} for i in ors]
    # from pprint import pprint
    # for i in ors:
    #     pprint(i)
    # print(sellers.name)
    nam = getUserInfo(sellers.api_token)['name']
    # print(nam)
    return Response({'sellers': sls, 'selname':nam}, status=200)


@api_view(['POST'])
@authentication_classes([CookieJWTAuthentication])
def create_warehouse(request):
    data = request.data

    # Проверяем наличие обязательного поля 'name'
    name = data.get('name')
    if not name:
        return Response({'error': 'Поле "name" обязательно'}, status=400)

    # Создаем объект Storage
    st = Storage(
        owner=request.user,  # Используем request.user напрямую
        name=name,
        address=data.get('address', '')  # Используем значение по умолчанию, если адрес не указан
    )

    # Сохраняем объект
    try:
        st.save()
    except Exception as e:
        return Response({'error': str(e)}, status=400)

    # Возвращаем успешный ответ
    return Response({'status': 'success', 'id': st.id}, status=201)




@api_view(['POST'])
@authentication_classes([CookieJWTAuthentication])
def create_cell(request):
    try:
        data = request.data
        required_fields = ['name', 'wrh']
        
        # Проверка обязательных полей
        for field in required_fields:
            if field not in data:
                return Response({'error': f'Поле "{field}" обязательно'}, status=400)
        
        # Создание ячейки
        cell = StorageCell.objects.create(
            warehouse_id=data['wrh'],
            cell_code=data['name'],
            description=data.get('address', '')
        )
        
        return Response({'status': 'success', 'id': cell.id}, status=201)
        
    except Exception as e:
        logger.error(f"Ошибка при создании ячейки: {str(e)}")
        return Response({'error': 'Internal server error'}, status=500)


@api_view(['POST'])
@authentication_classes([CookieJWTAuthentication])
def send_stikers(request):
    data = request.data
    # data = {'sid':'3', 'id' : 3}
    # print(data)
    if len(data) > 0:
        slr = Sellers.objects.get(id = data['sid'])
        stiks = []
        barcs = []
        pst = createPostavks(slr.api_token, data['items'][0]['name'] + ' ' + str(date.today()))['id']
        # pst ='WB-GI-142092778'
        sleep(1)
        for i in data['items']:
            addOrderInPostavk(slr.api_token,pst,i['id'])
            stiks.append(int(i['id']))
            print(i['id'] + ' добавлено в поставку ', pst)
            barcs.append(str(i['barcode'])+'.pdf')
            sleep(0.1)
        stkr = getStiker(slr.api_token,stiks)
        stiks = []
        sleep(3)
        for i in stkr:
            stiks.append(i['file'])

        addPst2Del(slr.api_token, pst)
        sleep(15)
        pst_code = getPSTStiker(slr.api_token, pst)
        # print(stiks,barcs)
        # barcs = ['2039773628195']
        create(stiks, output_pdf='pdfs/{pst}.pdf',pst_stiker= pst_code, insert_pdf_list=barcs)

        try:
            file = open('pdfs/{pst}.pdf', 'rb')
        except FileNotFoundError:
            return HttpResponse("File not found", status=404)
        
        response = FileResponse(file, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="{pst}.pdf"'
        return response
    else:
        return Response({'sellers': 'empty'}, status=200)
    # return Response({'sellers': 'sls'}, status=200)

# @api_view(['POST'])
# @authentication_classes([CookieJWTAuthentication])
# def addNewSeller(request):
#     token = request.data.get('token')