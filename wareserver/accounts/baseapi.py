import requests
import json
from pprint import pprint
try:
    from barcodes import create, split_pdf_by_barcode, generate_pdf
except:
    from .barcodes import create, split_pdf_by_barcode, generate_pdf

# from ..sellersinfo.models import Warehouse

def splitPdf(file_name : str):
    return split_pdf_by_barcode(file_name)


def gen_selection_list(dt, sh_id):
    return generate_pdf(dt, sh_id)

def getUserInfo(token : str):
    url = 'https://common-api.wildberries.ru/api/v1/seller-info'
    headers = {
    'Authorization': token, 
    'Content-Type': 'application/json'
    }
    response = requests.get(url,headers=headers)

    return response.json() 
    


def getSimple(token : str, url : str, params =  {}):
    # url = 'https://common-api.wildberries.ru/api/v1/seller-info'
    headers = {
    'Authorization': token,  # Замените YOUR_ACCESS_TOKEN на ваш токен
    'Content-Type': 'application/json'  # Пример другого заголовка
    }
    
    response = requests.get(url,headers=headers, params=params)

    if response.status_code == 200:
        print('Успешный запрос!')
        return response.json()  # Если ответ в формате JSON
    else:
        print('Ошибка:', response.status_code)
        return response.json()


def getPstInfo(token: str):
    result = []
    url = 'https://marketplace-api.wildberries.ru/api/v3/supplies'
    repeadParse = True

    # Заголовки
    headers = {
        'Authorization': token  # Если нужна авторизация
    }

    next_value = 0  # Начинаем с 0, как указано в документации

    while repeadParse:
        payload = {
            "limit": 1000,  # Максимальное значение, согласно документации
            "next": next_value
        }

        # Используем params для GET-запроса
        response = requests.get(url, params=payload, headers=headers)

        # Проверяем статус ответа
        if response.status_code != 200:
            print(f"Ошибка: {response.status_code}, {response.text}")
            break

        data = response.json()

        # Добавляем данные в результат
        for oneCard in data['supplies']:
            # if not oneCard['done']:
                result.append(oneCard)

        # Обновляем значение next для следующего запроса
        next_value = data.get('next', 0)

        # Проверяем, есть ли еще данные
        if len(data['supplies']) == 0:
            repeadParse = False

    return result


def getFBSorders(token : str):
    url = 'https://marketplace-api.wildberries.ru/api/v3/orders/new'
    headers = {
    'Authorization': token,  # Замените YOUR_ACCESS_TOKEN на ваш токен
    'Content-Type': 'application/json'  # Пример другого заголовка
    }
    response = requests.get(url,headers=headers)

    if response.status_code == 200:
        # print(response.text)

        return response.json()  # Если ответ в формате JSON
    else:
        print('Ошибка:', response.status_code)
        return response.text


def getStiker(token : str, ords : list) -> list:
    url = 'https://marketplace-api.wildberries.ru/api/v3/orders/stickers'


    headers = {
        'Content-Type': 'application/json',
        'Authorization': token 
    }

    params = {
    "type": "png", 
    "width": 58, 
    "height": 40    
    }
    
    payload = {
        "orders": ords
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers, params=params)

    return response.json().get('stickers')


def getPSTStiker(token : str, pst : str):
    url = f"https://marketplace-api.wildberries.ru/api/v3/supplies/{pst}/barcode"
    headers = {
        "Authorization": token
    }
    params = {
        "type": 'png'
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        # Возвращаем содержимое ответа (например, изображение или SVG)
        return response.json()['file']
    else:
        # В случае ошибки возвращаем None и выводим статус код
        print(f"Ошибка: {response.text}")
        return None


def createPostavks(token : str, name: str):
    url = 'https://marketplace-api.wildberries.ru/api/v3/supplies'


    # Заголовки (если нужны)
    headers = {
        'Content-Type': 'application/json',  # Указываем, что отправляем JSON
        'Authorization': token # Если нужна авторизация
    }

    
    # Отправка POST-запроса
    payload = {
    "name": name
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.json()


def addOrderInPostavk(token : str, pstId : str, ordId : str):
    url = f"https://marketplace-api.wildberries.ru/api/v3/supplies/{pstId}/orders/{ordId}"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    response = requests.patch(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}


def addPst2Del(token : str, pstId : str):
    url = f"https://marketplace-api.wildberries.ru/api/v3/supplies/{pstId}/deliver"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    response = requests.patch(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}


def getOrderStatus(token : str, ids : list):
    url = 'https://marketplace-api.wildberries.ru/api/v3/orders/status'
    data = {
    "orders": ids
    }

    headers = {
        'Content-Type': 'application/json',  # Указываем, что отправляем JSON
        'Authorization': token # Если нужна авторизация
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)

    return response.json

import jwt
from datetime import datetime

def decode_jwt(token):
    try:
        # Декодируем токен без проверки подписи
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        # Расшифровка поля `s`
        if 's' in decoded:
            s = decoded['s']
            # print(s & (1 << 3))
            if (s & (1 << 4) and not (s & (1 << 30))):
                decoded['available_categories'] = True
            else:
                decoded['available_categories'] = False
        
        # Преобразуем время жизни токена (exp) в удобный формат
        if 'exp' in decoded:
            exp_timestamp = decoded['exp']
            exp_datetime = datetime.fromtimestamp(exp_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            decoded['exp_formatted'] = exp_datetime
        
        return decoded
    except jwt.InvalidTokenError:
        return "er"

import requests

def get_supply_orders(api_key, supply_id):
    """
    Получает сборочные задания, закреплённые за поставкой.

    :param supply_id: ID поставки (например, "WB-GI-1234567").
    :param api_key: API-ключ для авторизации.
    :return: JSON-ответ с данными или сообщение об ошибке.
    """
    # URL для запроса
    url = f"https://marketplace-api.wildberries.ru/api/v3/supplies/{supply_id}/orders"
    
    # Заголовки запроса
    headers = {
        "Authorization": api_key,
        "Accept": "application/json"
    }
    
    try:
        # Выполняем GET-запрос
        response = requests.get(url, headers=headers)
        print(response.status_code)
        # Обрабатываем ответ
        if response.status_code == 200:
            # Успешный запрос, возвращаем JSON-ответ
            return response.json()
        elif response.status_code == 409:
            # Конфликт (например, поставка не готова к обработке)
            return {
                "error": "Конфликт (409): Поставка не готова к обработке.",
                "details": response.text
            }
        else:
            # Другие ошибки
            return {
                "error": f"Ошибка {response.status_code}",
                "details": response.text
            }
    except requests.exceptions.RequestException as e:
        # Обработка ошибок сети
        return {
            "error": "Ошибка сети",
            "details": str(e)
        }


if __name__ == "__main__":
    pass

    # k = getPstInfo(tk_gh)
    # gso = get_supply_orders
    # # print(decoded_token)
    # data = {
    #     'orders': [
    #         {'scanPrice': None, 'orderUid': 'f2fc4b25e21f40cb8402b50861aba2e5', 'article': 'R134a', 'colorCode': '', 'rid': 'Da.f2fc4b25e21f40cb8402b50861aba2e5.0.0', 'createdAt': '2025-03-17T09:29:53Z', 'offices': ['Москва_Запад-Юг'], 'skus': ['2040632859018'], 'id': 3121502408, 'warehouseId': 1330747, 'nmId': 242871365, 'chrtId': 381230807, 'price': 1469000, 'convertedPrice': 8502633, 'currencyCode': 643, 'convertedCurrencyCode': 398, 'cargoType': 1, 'isZeroOrder': False, 'options': {'isB2B': False}},
    #         # Добавьте другие заказы...
    #     ]
    # }
    # shipment_id = "WB-GI-145370091"  # ID поставки

    # # Генерация PDF
    # buffer = generate_pdf(data, shipment_id)
    # with open('pdfs/a4.pdf', 'wb') as fil:
    #     fil.write(buffer.getvalue())
    

