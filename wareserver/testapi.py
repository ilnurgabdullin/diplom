import requests
import json
# from pprint import pprint
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


def getPstInfo(token : str):
    result = []
    url = 'https://marketplace-api.wildberries.ru/api/v3/supplies'
    repeadParse = True


    # Заголовки (если нужны)
    headers = {
        'Content-Type': 'application/json',  # Указываем, что отправляем JSON
        'Authorization': token # Если нужна авторизация
    }

    while repeadParse:
    # Отправка POST-запроса
        payload = {
            "limit":100,
            "next": 0
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)

        for oneCard in response.json()['supplies']:
            # print(oneCard.keys())
            result.append(
            oneCard
            )
        payload = {
            'next': response.json()['next'],
            'limit':100
            }
        
        if len(response.json()['supplies']) < 0:
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
    pass