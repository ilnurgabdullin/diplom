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
    'Authorization': token,  # Замените YOUR_ACCESS_TOKEN на ваш токен
    'Content-Type': 'application/json'  # Пример другого заголовка
    }
    response = requests.get(url,headers=headers)

    if response.status_code == 200:
        print('Успешный запрос!')
        return response.json()  # Если ответ в формате JSON
    else:
        print('Ошибка:', response.status_code)
        return response.text


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


def getStiker(token : str, ords : list):
    url = 'https://marketplace-api.wildberries.ru/api/v3/orders/stickers'


    # Заголовки (если нужны)
    headers = {
        'Content-Type': 'application/json',  # Указываем, что отправляем JSON
        'Authorization': token # Если нужна авторизация
    }

    params = {
    "type": "png",  # Тип стикера (svg, zplv, zplh, png)
    "width": 58,    # Ширина стикера (58 или 40)
    "height": 40    # Высота стикера (40 или 30)
    }
    
    # Отправка POST-запроса
    payload = {
        "orders": ords
    }
    # print(ords)

    response = requests.post(url, data=json.dumps(payload), headers=headers, params=params)
    # print(response.json())

    return response.json()['stickers']


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
        print(f"Ошибка: {response.status_code}")
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
            categories = {
                1: "Контент",
                2: "Аналитика",
                3: "Цены и скидки",
                4: "Маркетплейс",
                5: "Статистика",
                6: "Продвижение",
                7: "Вопросы и отзывы",
                9: "Чат с покупателями",
                10: "Поставки",
                11: "Возвраты покупателями",
                12: "Документы",
                30: "Токен только на чтение"
            }
            # Получаем список доступных категорий
            available_categories = [categories[bit] for bit in categories if s & (1 << bit)]
            decoded['available_categories'] = available_categories
        
        # Преобразуем время жизни токена (exp) в удобный формат
        if 'exp' in decoded:
            exp_timestamp = decoded['exp']
            exp_datetime = datetime.fromtimestamp(exp_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            decoded['exp_formatted'] = exp_datetime
        
        return decoded
    except jwt.InvalidTokenError:
        return "Неверный токен"

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
# Пример использования
    token = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1NzczMzI5MCwiaWQiOiIwMTk1OTUzOC1lZGM0LTc1YjEtYTZiZi1iN2NhYzljMmFlMWMiLCJpaWQiOjg2NTA0NTA2LCJvaWQiOjg1ODE2NiwicyI6MjYsInNpZCI6IjVmNjczMmFlLTdmNzEtNDNlMi04ZTIxLWRjN2E2ZWM4YzBkNyIsInQiOmZhbHNlLCJ1aWQiOjg2NTA0NTA2fQ.cmNJuGcDZtpJwVMxkHvHXtrDnj43Sf3-ejKhOypZQVmnyKWbiwN9Hk2xEU1ZEeGFUx5IbajFdU-WmjE3zdlEug"
    tk = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1ODE3NTQ1MiwiaWQiOiIwMTk1YWY5My1jNjU4LTcwMGYtYmEyNC1iMDQ5NmMzNDdmOGIiLCJpaWQiOjk2NjcxMjY3LCJvaWQiOjQxMjk2MzYsInMiOjAsInNpZCI6ImQ1OTIxMTE3LWU1NTAtNDk1MC04OWYxLWJhNDFmNGQ0YmY5MCIsInQiOnRydWUsInVpZCI6OTY2NzEyNjd9.CkwRDIvoIEduq1UXmp4-xdHnPRA_wfU0_a69yWNE8rJtlZOYHytdOHWroS0DoRk4o_EVPRew9n3mjfUrBVKTnA'
    tk_ice = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1NzczNDU3NCwiaWQiOiIwMTk1OTU0Yy04NDYzLTcxMWQtYWZmNS1jMTJiZGQwNjZhOWIiLCJpaWQiOjkyNjQ4MjMxLCJvaWQiOjExMTYwOTMsInMiOjI2LCJzaWQiOiJmZjRjNTRmYi03NDQ2LTQ1N2UtOWE4Ni05NTA2YmUyOTRmZmYiLCJ0IjpmYWxzZSwidWlkIjo5MjY0ODIzMX0.PPDf0VttnxH6qNBNhecyX5rdHzdqjr9jFchjfd7T6cbM-ArmvMsNskXauOQkwwVgXN8CoBsI751wN6a1CONFZQ'
    tk_gh = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1Nzc0MzQ1NiwiaWQiOiIwMTk1OTVkNC0wYTEwLTcxZTUtOGIzNi1hMGRmYzhkMDU2YzMiLCJpaWQiOjkzMjA5MjE2LCJvaWQiOjEzOTgwMjAsInMiOjI2LCJzaWQiOiJmOTlkYjlmYi1lY2JjLTRkZDQtOWQ0Mi1hYjIyOGU1NzQ1OTUiLCJ0IjpmYWxzZSwidWlkIjo5MzIwOTIxNn0.ZI5hjmG4olsdTxhevqAXMSej9ooMCCnzJPrQeIvkBhNSgV6fjl1g2xeryIhr_PN1YZFMrCYjdPgeF6kq6dv5yA'
    tk_asanov = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMTIwdjEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1MzgyOTEyOSwiaWQiOiIwMTk0YWM4NC0yNzEzLTcyZGUtODc3Zi02ODU2OWRjZGYwNWEiLCJpaWQiOjY5MjAyNzE3LCJvaWQiOjU0Njg4NSwicyI6MjYsInNpZCI6IjNhNTAwMTZkLWI2MjItNDQ3Yi04ZDRiLTA5OGU4NGRmOTFiNiIsInQiOmZhbHNlLCJ1aWQiOjY5MjAyNzE3fQ.kBOBEuAP4dUS4fP9SuM3aw7PwkgugQgmilGkFIvJnCDpiff3m6XednK76m1KnpT6c7LD-9lkbvCtPH5tpkl_8g'
    tk_assen = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMTIwdjEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1MzgyOTIzNSwiaWQiOiIwMTk0YWM4NS1jMzg4LTc4NTQtOTBmZC01NjcwMDY0ZDYwNTMiLCJpaWQiOjY5MDUxNzM4LCJvaWQiOjY0MDY2NCwicyI6MjYsInNpZCI6ImVmYmZhNzUwLTZjMzgtNGMzNy04YTlmLTliZmIzZThkZjUxNyIsInQiOmZhbHNlLCJ1aWQiOjY5MDUxNzM4fQ.pN02_bCVQiioqszl8qWBVeKMbFwF-hkSOFtFur-NqURcxp7YT1kuuxfxb9aFb1PtCmLnJ-Heuw2ekMjHb-kc1Q'
    tk_tygay = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMTIwdjEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1MzkyMjYwMiwiaWQiOiIwMTk0YjIxNi02ZWNkLTc1YWUtYWVjOC0xNTM0OGMxMDY4MDciLCJpaWQiOjE5Mjg1MjYwMSwib2lkIjo0Mjg2Mjc4LCJzIjoxOCwic2lkIjoiNDhmMTNmOWYtNzdkMy00NmVjLWEyODItMTJjYjk3OTBiNDNhIiwidCI6ZmFsc2UsInVpZCI6MTkyODUyNjAxfQ.e0RizWsv1mMY3bUL4fmXb8w69SjJ1c7tp21GRVelDwURv5m6qQ2VYvKUW_UvpOoUWII-Du8V8PNtYc2eIFsAOg'
    # decoded_token = decode_jwt(tk)
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
    

