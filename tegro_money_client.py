import hmac
from hashlib import sha256
import json
from time import time
import requests
from tegro_config import SHOP_ID, SECRET_KEY, API_KEY


class TegroMoneyClient:
    BASE_URL = "https://tegro.money/api"
    nonce = int(time())
    base_data = {
        "shop_id": SHOP_ID,
        "nonce": nonce,
    }

    # Создание подписи запроса
    @staticmethod
    def create_sign(data):
        # print(str.encode(data))
        sign = hmac.new(str.encode(API_KEY), str.encode(data), sha256).hexdigest()
        return sign

    # Запрос к API
    @staticmethod
    def make_request(url: str, body: str):
        return requests.post(
            TegroMoneyClient.BASE_URL + url,
            headers={"Authorization": "Bearer " + TegroMoneyClient.create_sign(body),
                     "Content-Type": "application/json"},
            data=body
        )

    # Создание заказа
    def create_order(self, currency: str, amount: int, payment_system: int, order_id: str, test: int = 0,
                     fields: dict = None,
                     receipt: dict = None) -> dict:
        data = {
            **self.base_data,
            "currency": currency,
            "amount": amount,
            "order_id": order_id,
            "test": test,
            "payment_system": payment_system,
        }
        if fields:
            data["fields"] = fields
        if receipt:
            data["receipt"] = receipt
        body = json.dumps(data)
        resp = self.make_request("/createOrder/", body)
        return resp.json()

    @staticmethod
    # Получение списка магазинов
    def get_shops() -> dict:
        body = json.dumps(TegroMoneyClient.base_data)
        resp = TegroMoneyClient.make_request("/shops/", body)
        return resp.json()

    @staticmethod
    # Получение баланса всех кошельков
    def get_balance() -> dict:
        body = json.dumps(TegroMoneyClient.base_data)
        resp = TegroMoneyClient.make_request("/balance/", body)
        return resp.json()

    # Получение информации о заказе
    def get_order(self, order_id: int = None, payment_id: str = "") -> dict | str:
        data = self.base_data
        if not order_id and not payment_id:
            return "Должен быть указан номер платежа tegro.money или номер оплаты магазина"
        elif order_id:
            data["order_id"] = order_id
        else:
            data["payment_id"] = payment_id
        body = json.dumps(data)
        resp = self.make_request("/order/", body)
        return resp.json()

    # Получение информации о заказах
    def get_orders_list(self, page: int) -> dict:
        data = {
            **self.base_data,
            "page": page,
        }
        body = json.dumps(data)
        resp = self.make_request("/orders/", body)
        return resp.json()

    # Вывод средств
    def create_withdrawal(self, currency: str, account: str, amount: int, payment_id: str, payment_system: int) -> dict:
        data = {
            **self.base_data,
            "currency": currency,
            "account": account,
            "amount": amount,
            "payment_id": payment_id,
            "payment_system": payment_system,
        }
        body = json.dumps(data)
        resp = self.make_request("/createWithdrawal/", body)
        return resp.json()

    # Получение списка выплат
    def get_withdrawals_list(self, page: int) -> dict:
        data = {
            **self.base_data,
            "page": page,
        }
        body = json.dumps(data)
        resp = self.make_request("/withdrawals/", body)
        return resp.json()

    # Получение платежной информации
    def get_withdrawal(self, order_id: int = None, payment_id: str = "") -> dict | str:
        data = self.base_data
        if not order_id and not payment_id:
            return "Должен быть указан номер платежа tegro.money или номер оплаты магазина"
        elif order_id:
            data["order_id"] = order_id
        else:
            data["payment_id"] = payment_id
        body = json.dumps(data)
        resp = self.make_request("/withdrawal/", body)
        return resp.json()

tc = TegroMoneyClient()

# Тестовые данные
fields = {
    "email": "user@email.ru",
    "phone": "79111231212",
}
receipt = {
    "items": [
        {
            "name": "test item 1",
            "count": 1,
            "price": 600
        },
        {
            "name": "test item 2",
            "count": 1,
            "price": 600
        }
    ]
}
# Вывод результатов тестовых запросов
print(tc.create_order("RUB", 1200, 5, "test order", 1, fields, receipt))
print(tc.get_shops())
print(tc.get_balance())
print(tc.get_order(payment_id="test order"))
print(tc.get_orders_list(1))
print(tc.create_withdrawal("RUB", "56555+rthyhfj", 120, "test pay", 36))
print(tc.get_withdrawal(payment_id="test order"))
