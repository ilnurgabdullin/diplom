import requests
import json
from pprint import pprint
try:
    from accounts.barcodes import create, split_pdf_by_barcode
except:
    from .barcodes import create, split_pdf_by_barcode

# from ..sellersinfo.models import Warehouse

def splitPdf(file_name : str):
    return split_pdf_by_barcode(file_name)

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
            if not oneCard['done']:
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

    
def wb_con():

    url = "https://01-etiketka.wbcon.su/put?email=ilnurgabdullin627@gmail.com&password=9n9BC2VA"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    data = {
        "viewBarcode": True,
        "barcode": "45896325",
        "name": "Обувь Кроссовки",
        "article": "4589633258",
        "manuf_name": "",
        "brand": "БелвестОбувь",
        "size": "",
        "color": "",
        "font_size": 11,
        "field_free": "",
        "width": 58,
        "height": 40
}

    response = requests.post(url, json=data, headers=headers, verify=False)

    print(response.status_code)  # Выводит статус ответа
    print(response.json())  # Выводит JSON-ответ сервера


if __name__ == "__main__":
    tk1 = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1NzczNDU3NCwiaWQiOiIwMTk1OTU0Yy04NDYzLTcxMWQtYWZmNS1jMTJiZGQwNjZhOWIiLCJpaWQiOjkyNjQ4MjMxLCJvaWQiOjExMTYwOTMsInMiOjI2LCJzaWQiOiJmZjRjNTRmYi03NDQ2LTQ1N2UtOWE4Ni05NTA2YmUyOTRmZmYiLCJ0IjpmYWxzZSwidWlkIjo5MjY0ODIzMX0.PPDf0VttnxH6qNBNhecyX5rdHzdqjr9jFchjfd7T6cbM-ArmvMsNskXauOQkwwVgXN8CoBsI751wN6a1CONFZQ'
    tk2 = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1Nzc0MzQ1NiwiaWQiOiIwMTk1OTVkNC0wYTEwLTcxZTUtOGIzNi1hMGRmYzhkMDU2YzMiLCJpaWQiOjkzMjA5MjE2LCJvaWQiOjEzOTgwMjAsInMiOjI2LCJzaWQiOiJmOTlkYjlmYi1lY2JjLTRkZDQtOWQ0Mi1hYjIyOGU1NzQ1OTUiLCJ0IjpmYWxzZSwidWlkIjo5MzIwOTIxNn0.ZI5hjmG4olsdTxhevqAXMSej9ooMCCnzJPrQeIvkBhNSgV6fjl1g2xeryIhr_PN1YZFMrCYjdPgeF6kq6dv5yA'
    tk3 = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1NzczMzI5MCwiaWQiOiIwMTk1OTUzOC1lZGM0LTc1YjEtYTZiZi1iN2NhYzljMmFlMWMiLCJpaWQiOjg2NTA0NTA2LCJvaWQiOjg1ODE2NiwicyI6MjYsInNpZCI6IjVmNjczMmFlLTdmNzEtNDNlMi04ZTIxLWRjN2E2ZWM4YzBkNyIsInQiOmZhbHNlLCJ1aWQiOjg2NTA0NTA2fQ.cmNJuGcDZtpJwVMxkHvHXtrDnj43Sf3-ejKhOypZQVmnyKWbiwN9Hk2xEU1ZEeGFUx5IbajFdU-WmjE3zdlEug'
    tk4 = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMTIwdjEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1Mzk5Njg4MSwiaWQiOiIwMTk0YjY4My1kNzY2LTdiY2UtOTM3Mi05MmUyODY3OWQzMmIiLCJpaWQiOjkwNDEyNTAxLCJvaWQiOjEwNTY4MjYsInMiOjI2LCJzaWQiOiI3N2EzODBhOC04MTEwLTQ2YjEtOGI1Ni01OWE3MmQyNDNhODUiLCJ0IjpmYWxzZSwidWlkIjo5MDQxMjUwMX0.Zj9bjLv4NGSGhZBi6MeUw45vnMrP8PUdnfvSnNGS4A5EZXAtJxJBiVLeTJPG9HB_F2f2PDWRnSKILfr_XyUqFw'
    pass
    print(getPstInfo(tk2))