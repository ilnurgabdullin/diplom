# from rest_framework import generics, permissions
from rest_framework.response import Response
# from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import HttpResponse, FileResponse
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated # type: ignore
from rest_framework.response import Response
from sellersinfo.models import Sellers, Cards, InfoModel, Warehouse
# from accounts.models import CustomUser
# from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
# from rest_framework import status
from datetime import timedelta
from django.conf import settings
from django.shortcuts import render
from wareserver.authentication import CookieJWTAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from accounts.baseapi import getSimple, getStiker, getFBSorders, createPostavks, addOrderInPostavk, getPSTStiker, addPst2Del
from accounts.barcodes import create
# from .models import Sellers
from datetime import date
from time import sleep


@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def user_inform(request):
    # Твоя логика здесь
    # user = request.user  # Получаем данные о пользователе
    return render(request, 'mainProfile.html')


@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def seller_profile(request, seller_id):
    return render(request, 'profile.html', {'seller_id': seller_id})



@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def fbs_orders(request, seller_id):
    # user = request.user  # Получаем данные о пользователе
    # user = CustomUser.objects.get(id=user.id)
    sellers = Sellers.objects.get(id=seller_id) # Получаем всех связанных продавцов
    # print(Warehouse.objects.get())

    ors = getFBSorders(sellers.api_token)['orders'] #,'https://marketplace-api.wildberries.ru/api/v3/orders/new')['orders']
    sls = [{'id':i['id'], 'name':Warehouse.objects.get(location_id=i['warehouseId']).name, 'skus':i['skus'][0]} for i in ors]
    # print(sellers.name)
    return Response({'sellers': sls}, status=200)

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
        sleep(0.5)
        for i in data['items']:
            addOrderInPostavk(slr.api_token,pst,i['id'])
            stiks.append(int(i['id']))
            print(i['id'] + ' добавлено в поставку ', pst)
            barcs.append(str(i['barcode'])+'.pdf')
            sleep(0.1)
        # stiks = [3052787217]
        stkr = getStiker(slr.api_token,stiks)
        stiks = []
        sleep(2)
        for i in stkr:
            stiks.append(i['file'])
        # print(pst_code.keys()) # pst_stiker= pst_code['file']
        # sleep(1)
        ln = getSimple(slr.api_token, 'https://marketplace-api.wildberries.ru/api/v3/supplies/{pst}/orders')['orders']
        while ln < len(stkr):
            ln = getSimple(slr.api_token, 'https://marketplace-api.wildberries.ru/api/v3/supplies/{pst}/orders')['orders']

        addPst2Del(slr.api_token, pst)
        sleep(3)
        pst_code = getPSTStiker(slr.api_token, pst)
        # print(stiks,barcs)
        # barcs = ['2039773628195']
        create(stiks, output_pdf='pdfs/ord.pdf',pst_stiker= pst_code, insert_pdf_list=barcs)

        try:
            file = open('pdfs/ord.pdf', 'rb')
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