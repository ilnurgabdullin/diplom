from django.shortcuts import render
# from rest_framework import generics, permissions
from rest_framework.response import Response
# from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserRegistrationSerializer, MyTokenObtainPairSerializer
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sellersinfo.models import Sellers, Cards, InfoModel, Warehouse
from accounts.models import CustomUser
from .baseapi import getUserInfo, getCardInfo, getSimple, splitPdf
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import MyTokenObtainPairSerializer
from datetime import timedelta
# from django.conf import settings
from wareserver.authentication import CookieJWTAuthentication
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse

@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
# @permission_classes([IsAuthenticated])
def my_custom_view(request):
    # Твоя логика здесь
    
    user = request.user  # Получаем данные о пользователе
    user = CustomUser.objects.get(id=user.id)
    sellers = Sellers.objects.filter(info__userId=user)  # Получаем всех связанных продавцов
    sls = [{'name': i.name, 'trademark': i.trademark, 'id' : i.id} for i in sellers]
    return Response({'sellers': sls}, status=200)



@api_view(['POST'])
@authentication_classes([CookieJWTAuthentication])
def upload_pdf(request):
    pdf_file = request.FILES['pdf_file']

        # Проверяем, что файл является PDF
    if not pdf_file.name.endswith('.pdf'):
        return HttpResponse('Ошибка: разрешены только PDF-файлы.', status=400)

        # Генерируем уникальное имя для файла
    # unique_name = f"{uuid.uuid4().hex}.pdf"
    file_path = os.path.join('pdfs', pdf_file.name)

        # Сохраняем файл в папку media/pdfs/
    default_storage.save(file_path, ContentFile(pdf_file.read()))

        # Если используется модель, сохраняем информацию в базу данных
        # PDFFile.objects.create(file=file_path)

    return HttpResponse('Файл успешно загружен!')

@api_view(['POST'])
@authentication_classes([CookieJWTAuthentication])
def addNewSeller(request):
    token = request.data.get('token')
    if not token:
        return Response({'error': 'Токен не передан'}, status=400)

    dt = getUserInfo(token)  # Получаем данные продавца
    try:
        updateWarehouses(token)
    except:
        pass
    # Проверяем, есть ли уже продавец с таким sid
    seller, created = Sellers.objects.get_or_create(
        sid=dt['sid'],
        defaults={
            'name': dt['name'],
            'trademark': dt.get('tradeMark', ''),
            'api_token': token
        }
    )

    # Проверяем, есть ли уже запись в InfoModel для этого пользователя и продавца
    user = request.user  # Получаем пользователя из запроса
    info_exists = InfoModel.objects.filter(userId=user, sellerId=seller).exists()

    if not info_exists:
        # Если связки пользователя с продавцом нет — создаем
        InfoModel.objects.create(userId=user, sellerId=seller)

    # Если продавец новый — загружаем карточки
    if created:
        cards_data = getCardInfo(token)
        cards_to_create = [
            Cards(
                seller=seller,
                nmid=cr['nmid'],
                imtid=cr['imtid'],
                nmuuid=cr['nmuuid'],
                subjectid=cr['subjectid'],
                subjectname=cr['subjectname'],
                vendorcode=cr['vendorcode'],
                brand=cr['brand'],
                title=cr['title'],
                description=cr['description'],
                needkiz=cr['needkiz'],
                createdat=cr['createdat'],
                updatedat=cr['updatedat'],
            )
            for cr in cards_data
        ]
        Cards.objects.bulk_create(cards_to_create)  # Создаём все карточки одним запросом

    return Response({'response': 'Продавец добавлен или уже существует'})




@api_view(['POST'])
@permission_classes([AllowAny])
def user_registration_view(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_205_RESET_CONTENT)


@api_view(['POST'])
@authentication_classes([CookieJWTAuthentication])
def newFile(request):
    
        # Проверяем, есть ли файл в запросе
    if 'myfile' not in request.FILES:
        return JsonResponse({'error': 'Файл не найден в запросе'}, status=400)

    uploaded_file = request.FILES['myfile']  # Получаем файл

        # Проверяем, что файл имеет расширение .pdf
    if not uploaded_file.name.endswith('.pdf'):
        return JsonResponse({'error': 'Файл должен быть в формате PDF'}, status=400)

    file_path = os.path.join('pdfs', uploaded_file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    names=splitPdf(file_path)
    try:
        os.remove(file_path)
    except:
        pass
    return JsonResponse({'message': 'Файл успешно загружен', 'file_path': names})
    


@api_view(['POST'])
@permission_classes([AllowAny])  # Разрешаем доступ всем
def my_token_obtain_pair_view(request):
    if request.method == 'POST':
        # Используем ваш кастомный сериализатор
        serializer = MyTokenObtainPairSerializer(data=request.data)
        
        if serializer.is_valid():
            # Если данные валидны, возвращаем токены
            tokens = serializer.validated_data

            # Получаем access и refresh токены
            access_token = tokens['access']
            refresh_token = tokens['refresh']

            # Настройки для кук
            access_token_expiry = timedelta(days = 1)  # Устанавливаем время жизни для access_token (например, 15 минут)
            refresh_token_expiry = timedelta(days=7)  # Устанавливаем время жизни для refresh_token (например, 7 дней)

            # Отправляем токены в куки
            response = Response(tokens, status=status.HTTP_200_OK)

            # Устанавливаем access_token в куки
            response.set_cookie(
                'access_token', 
                access_token, 
                max_age=access_token_expiry, 
                httponly=True,  # Защищает куки от доступа через JavaScript
                # secure=True,    # Куки отправляются только по HTTPS
                samesite='Strict'  # Куки отправляются только для запросов на тот же сайт
            )

            # Устанавливаем refresh_token в куки
            response.set_cookie(
                'refresh_token', 
                refresh_token, 
                max_age=refresh_token_expiry, 
                httponly=True, 
                # secure=True, 
                samesite='Strict'
            )

            return response
        
        # Если данные невалидны, возвращаем ошибки
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([AllowAny])
def user_auth_view(request):
    return render(request, 'auth.html')  # Отдаём HTML-шаблон




def updateWarehouses(tk):
    cards_data = getSimple(tk,'https://marketplace-api.wildberries.ru/api/v3/warehouses')
    cards_to_create = [
            Warehouse(
                name = cr['name'],
                location_id = cr['id'],
                office_id = cr['officeId'],
                cargo_type = cr['cargoType'],
                delivery_type = cr['deliveryType']
               
            )
            for cr in cards_data
        ]
    Warehouse.objects.bulk_create(cards_to_create)




# tk = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMTIwdjEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1MzkyMjYwMiwiaWQiOiIwMTk0YjIxNi02ZWNkLTc1YWUtYWVjOC0xNTM0OGMxMDY4MDciLCJpaWQiOjE5Mjg1MjYwMSwib2lkIjo0Mjg2Mjc4LCJzIjoxOCwic2lkIjoiNDhmMTNmOWYtNzdkMy00NmVjLWEyODItMTJjYjk3OTBiNDNhIiwidCI6ZmFsc2UsInVpZCI6MTkyODUyNjAxfQ.e0RizWsv1mMY3bUL4fmXb8w69SjJ1c7tp21GRVelDwURv5m6qQ2VYvKUW_UvpOoUWII-Du8V8PNtYc2eIFsAOg'
    
# # updateWarehouses(tk)