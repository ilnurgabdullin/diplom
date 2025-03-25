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
from .baseapi import getUserInfo, getSimple, splitPdf
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
    st = getSimple(token, url='https://marketplace-api.wildberries.ru/ping')
    

    # Ищем продавца по sid
    seller, created = Sellers.objects.get_or_create(
        sid=dt['sid'],  # Проверяем по sid
        defaults={
            'name': dt['name'],
            'trademark': dt.get('tradeMark', ''),
            'api_token': token
        }
    )

    # Если запись уже существует, обновляем токен
    if not created:
        seller.api_token = token
        seller.save()

    # Проверяем, есть ли уже запись в InfoModel для этого пользователя и продавца
    user = request.user  # Получаем пользователя из запроса
    
    info_exists = InfoModel.objects.filter(userId=user, sellerId=seller).exists()
    try:
        # print(user)
        updateWarehouses(token, userId=CustomUser.objects.get(username=user).id)
    except Exception as ex:
        print('errorororoor: ',ex)
    if not info_exists:
        # Если связки пользователя с продавцом нет — создаем
        InfoModel.objects.create(userId=user, sellerId=seller)


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
            
           

            # Отправляем токены в куки
            response = Response(tokens, status=status.HTTP_200_OK)

            # Устанавливаем access_token в куки
            response.set_cookie(
                'access_token', 
                access_token, 
                max_age=3600, 
                httponly=True,  # Защищает куки от доступа через JavaScript
                # secure=True,    # Куки отправляются только по HTTPS
                samesite='Strict'  # Куки отправляются только для запросов на тот же сайт
            )

            # Устанавливаем refresh_token в куки
            response.set_cookie(
                'refresh_token', 
                refresh_token, 
                max_age=3600*24, 
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




def updateWarehouses(tk, userId):
    cards_data = getSimple(tk,'https://marketplace-api.wildberries.ru/api/v3/warehouses')
    cards_to_create = [
            Warehouse(
                name = cr['name'],
                location_id = cr['id'],
                office_id = cr['officeId'],
                cargo_type = cr['cargoType'],
                delivery_type = cr['deliveryType'],
                owner_id = userId
               
            )
            for cr in cards_data
        ]
    Warehouse.objects.bulk_create(cards_to_create)

