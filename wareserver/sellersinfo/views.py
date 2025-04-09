from rest_framework.response import Response
from rest_framework.response import Response
from sellersinfo.models import Sellers, Cards, InfoModel, Warehouse, Storage, StorageCell, ProductPlacement
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from wareserver.authentication import CookieJWTAuthentication
from rest_framework.decorators import api_view, authentication_classes
from accounts.baseapi import getStiker, getFBSorders, createPostavks, addOrderInPostavk, getPSTStiker, addPst2Del, getUserInfo, get_supply_orders, getPstInfo
from accounts.barcodes import create, generate_pdf
from datetime import date
from time import sleep
import logging
from django.db.models import Prefetch
logger = logging.getLogger(__name__)
from django.http import JsonResponse
from django.core.exceptions import ValidationError
import os


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
                    'name': placement.product.subjectname,
                    'quantity': placement.quantity,
                    'article': placement.product.vendorcode
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

@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def user_inform(request):
    return render(request, 'sellerlistMain.html')


@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def my_warehouse_template(request):
    return render(request, 'my_warehouse.html')


@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def goods_template(request):
    return render(request, 'goods.html')


@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
# @permission_classes([IsAuthenticated])
def myProfile(request):
    # Твоя логика здесь
    return render(request, 'settings.html')


@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def seller_profile(request, seller_id):
    return render(request, 'orders.html', {'seller_id': seller_id})


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
def get_goods(request):
    sellers_queryset = Sellers.objects.filter(info__userId_id=request.user).distinct()
    goods_info = []
    for i in sellers_queryset:
        goods = [ {'barc':j.vendorcode, 'name':j.subjectname} for j in Cards.objects.filter(seller_id=i.sid, user_id = request.user.id)]
        goods_info.append({
            'name' : i.name,
            'mark' : i.trademark,
            'sel_id' : i.id,
            'goods': goods
        })
    # print(goods_info)
    return Response({'all_goods': goods_info}, status=200)


@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def get_my_storages(request):
    storages = Storage.objects.filter(owner=request.user.id)
    # print(storages)
    sts = [{'id':i.id, 'name':i.name} for i in storages]
    # print(sts)
    return Response({'storages': sts}, status=200)


@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def fbs_orders(request, seller_id):
    sellers = Sellers.objects.get(id=seller_id) # Получаем всех связанных продавцов
    ors = getFBSorders(sellers.api_token)['orders']
    user_id = request.user.id
    sls = [{'id':i['id'], 'art':i['article'],'name':Warehouse.objects.get(location_id=i['warehouseId']).name, 'skus':i['skus']} for i in ors]
    print(sls)
    for i in sls:
        try:
            new_product = create_product(
                user_id = user_id,
                name=i['art'],
                seller_id=seller_id,
                vendorcode=int(i['skus'][0])
            )
            print(f"Создан товар с ID {new_product.id}")
        except ValidationError as e:
            print(f"Ошибка: {e}")
        except:
            print("Продавец не найден")
    nam = getUserInfo(sellers.api_token)['name']
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


from django.shortcuts import get_object_or_404

@api_view(['POST'])
@authentication_classes([CookieJWTAuthentication])
def add_good(request):
    data = request.data
    
    # Проверяем наличие обязательных полей
    name = data.get('name')
    seller_id = data.get('seller_id')
    vendorcode = data.get('vendorcode')
    print(data)
    # Валидация входных данных
    if not name or not seller_id:
        return Response({'error': 'Поля "name" и "seller_id" обязательны'}, status=400)
    
    try:
        # Вызываем функцию создания товара
        new_product = create_product(
            user_id = request.user.id,
            name=name,
            seller_id=seller_id,
            vendorcode=vendorcode
        )
        
        return Response({
            'status': 'success',
            'id': new_product.id,
            'name': new_product.subjectname,
            'vendorcode': new_product.vendorcode
        }, status=201)
        
    except Exception as e:
        print(e)
        return Response({'error': str(e)}, status=400)


def create_product(user_id,name, seller_id, vendorcode=None):
    if vendorcode and Cards.objects.filter(vendorcode=vendorcode, user_id = user_id).exists():
        raise ValidationError(f'Товар с vendorcode "{vendorcode}" уже существует')
    
    seller = get_object_or_404(Sellers, id=seller_id)
    
    product, created = Cards.objects.get_or_create(
    user_id=user_id,
    vendorcode=vendorcode,
    defaults={
        'seller': seller,
        'subjectname': name
    }
)
    if not created:
        raise ValidationError('Ошибка')
    product.save()
    
    return product

@api_view(['POST'])
@authentication_classes([CookieJWTAuthentication])
def update_good(request):
    print(request.data)
    number = Cards.objects.filter(
        vendorcode=request.data.get('goodId'),
        user_id=request.user.id
        ).update(subjectname=request.data.get('newName'))
    print(number)
    return Response({'status': number}, status=200)

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
def add_product_to_cell(request):
    try:
        data = request.data
        user = request.user
        
        # Получаем необходимые данные из запроса
        wrh_id = data.get('wrh_id')  # ID склада (Storage)
        cell_id = data.get('cell_id')  # ID ячейки (StorageCell)
        barcode = data.get('barcode')  # Штрих-код товара (vendorcode в Cards)
        quantity = data.get('quantity', 1)  # Количество, по умолчанию 1

        # Валидация входных данных
        if not all([wrh_id, cell_id, barcode]):
            return Response({'error': 'Missing required fields'}, status=400)

        # Проверяем существование склада и принадлежность пользователю
        try:
            storage = Storage.objects.get(id=wrh_id, owner=user)
        except Storage.DoesNotExist:
            return Response({'error': 'Storage not found or access denied'}, status=404)

        # Проверяем существование ячейки и принадлежность складу
        try:
            cell = StorageCell.objects.get(id=cell_id, warehouse=storage)
        except StorageCell.DoesNotExist:
            return Response({'error': 'Cell not found or does not belong to this storage'}, status=404)

        # Ищем товар по штрих-коду среди продавцов пользователя
        try:
            # Получаем всех продавцов пользователя
            user_sellers = InfoModel.objects.filter(userId=user).values_list('sellerId', flat=True)
            
            # Ищем товар у этих продавцов
            product = Cards.objects.get(
                vendorcode=barcode,
                user_id = request.user.id,
                seller__sid__in=user_sellers
            )
        except Cards.DoesNotExist:
            return Response({'error': 'Product not found or you dont have access to it'}, status=404)
        except Cards.MultipleObjectsReturned:
            return Response({'error': 'Multiple products found with this barcode'}, status=400)

        # Проверяем, не добавлен ли уже этот товар в эту ячейку
        placement, created = ProductPlacement.objects.get_or_create(
            product=product,
            cell=cell,
            defaults={'quantity': quantity}
        )

        if not created:
            # Если товар уже есть в ячейке - увеличиваем количество
            placement.quantity += int(quantity)
            placement.save()

        return Response({
            'status': 'success',
            'product': {
                'id': product.id,
                'name': product.subjectname,
                'vendorcode': product.vendorcode
            },
            'cell': {
                'id': cell.id,
                'code': cell.cell_code
            },
            'quantity': placement.quantity
        }, status=201 if created else 200)
        
    except Exception as e:
        logger.error(f"Ошибка при добавлении товара в ячейку: {str(e)}", exc_info=True)
        return Response({'error': 'Internal server error'}, status=500)



@api_view(['POST'])
@authentication_classes([CookieJWTAuthentication])
def send_stikers(request):
    data = request.data
    if len(data) > 0:
        slr = Sellers.objects.get(id = data['sid'])
        pst = createPostavks(slr.api_token, data['items'][0]['name'] + ' ' + str(date.today()))['id']
        sleep(1)
        for i in data['items']:
            addOrderInPostavk(slr.api_token,pst,i['id'])
            sleep(0.5)

        addPst2Del(slr.api_token, pst)
        return Response({'spl_id': pst}, status=200)
    else:
        return Response({'sellers': 'empty'}, status=200)



@api_view(['POST'])
@authentication_classes([CookieJWTAuthentication])
def get_podbor_list(request):
    data = request.data
    pst = data.get('supply',False)
    if pst:
        stiker_file = os.path.join("pdfs","stikers",pst)+'.pdf'
        sheet_file = os.path.join("pdfs","supplies",pst)+'.pdf'
        print(stiker_file, sheet_file)
        print(os.path.isfile(stiker_file), os.path.isfile(sheet_file))
    else:
        return Response({'sellers': 'empty'}, status=200)
    
    if os.path.isfile(stiker_file) and os.path.isfile(sheet_file):
        print('файлы уже есть')
        return Response({'sellers': 'ok'}, status=200)
    else:
        slr = Sellers.objects.get(id = data['seller'])
        slr_tk = slr.api_token
        slr_name = slr.name
        
        ords = get_supply_orders(slr_tk, pst)
        ids = []
        barcs_list = []
        for i in ords['orders']:
            ids.append(i['id'])
            barcs_list.append(i.get('skus',[''])[0])
        try:
            sticks = getStiker(slr_tk, ids)
        except:
            sticks = []

        barcs = get_products_with_placements(set(barcs_list))
        stiks = []
        sleep(2)
        for i in sticks:
            stiks.append(i.get('file',''))
        pst_code = getPSTStiker(slr.api_token, pst)
        print(len(barcs_list), len(sticks))
        create(stiks, output_pdf=f'pdfs/stikers/{pst}.pdf',pst_stiker= pst_code, insert_pdf_list=barcs_list)
        data_for_list = []
        print(barcs)
        for ord, stik in zip(ords['orders'],sticks):
            k = ord.get('skus',['null'])[0]
            # print(k,barcs.get(k))
            data_for_list.append(
                {
                    'id':ord.get('id','null'),
                    'cell':barcs.get(k,{'name': 'нет информации о товаре'}).get('placements',['не добавлено в ячейку'])[0],
                    'name':barcs.get(k,{'name': 'нет информации о товаре'})['name'],
                    'barc': k,
                    'stik':stik['partA']+stik['partB']
                }
            )
        print(data_for_list)
        print(generate_pdf(data_for_list, pst+'#'+slr_name))
        return Response({'sellers': 'empty'}, status=200)


from django.http import FileResponse
import os

@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def get_stikers(request, sticker_id):
    print(sticker_id)
    if os.path.join("pdfs","stikers",sticker_id)+'.pdf':
        filepath = os.path.join('pdfs','stikers',sticker_id) + '.pdf'
        return FileResponse(open(filepath, 'rb'), content_type='application/pdf')
    else:
        return Response({'sellers': 'empty'}, status=200)



@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
def get_supplies(request, sticker_id):
    print(sticker_id)
    if os.path.join("pdfs","supplies",sticker_id)+'.pdf':
        filepath = os.path.join('pdfs','supplies',sticker_id) + '.pdf'
        return FileResponse(open(filepath, 'rb'), content_type='application/pdf')
    else:
        filepath = os.path.join('pdfs','supplies',sticker_id) + '.pdf'
        return FileResponse(open(filepath, 'rb'), content_type='application/pdf')


def get_products_with_placements(vendor_codes):
    products = (
        Cards.objects
        .filter(vendorcode__in=vendor_codes)
        .prefetch_related(
            Prefetch(
                'placements',  # related_name в ProductPlacement
                queryset=ProductPlacement.objects.select_related(
                    'cell__warehouse'  # цепочка: ProductPlacement → StorageCell → Storage
                )
            )
        )
    )

    result = {}
    
    for product in products:
        placements_info = []
        
        for placement in product.placements.all():  # Уже загружено благодаря prefetch_related
            cell = placement.cell
            placements_info.append(cell.cell_code)
        
        if placements_info:
            result[product.vendorcode] = {'name': product.subjectname, 'placements': placements_info}
        else:
            result[product.vendorcode] = {'name': product.subjectname}  # или просто не добавлять
    
    return result

