import time
import hmac
import base64
import hashlib
import requests
import json
from urllib.parse import urlencode, urlparse

class BitgetFuturesClient:
    def __init__(self, api_key, api_secret, passphrase, debug=True):
        """
        Инициализация Bitget API клиента для фьючерсов.

        :param api_key: Ваш API ключ Bitget
        :param api_secret: Ваш секретный ключ Bitget
        :param passphrase: Ваш passphrase Bitget
        :param debug: True для вывода отладочной информации
        """
        self.api_key = api_key.strip()
        self.api_secret = api_secret.strip()
        self.passphrase = passphrase.strip()
        self.debug = debug
        # Базовый URL для фьючерсного API (например, для USDT‑фьючерсов)
        self.base_url = "https://api.bitget.com/api/mix/v1"
        self.session = requests.Session()

    def _generate_signature(self, timestamp, method, request_path, body=''):
        """
        Генерирует подпись для аутентификации.

        :param timestamp: Текущее время в миллисекундах
        :param method: HTTP метод (GET, POST и т.д.)
        :param request_path: Полный путь запроса (например, "/api/mix/v1/account/accounts")
        :param body: Тело запроса (для POST)
        :return: Подпись (Base64-encoded)
        """
        body_str = json.dumps(body) if body else ''
        message = str(timestamp) + method.upper() + request_path + body_str
        if self.debug:
            print(f"DEBUG: Signature message: {message}")
        signature = base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        return signature

    def _request(self, method, endpoint, params=None, data=None, skip_auth=False):
        url = self.base_url + endpoint
        timestamp = str(int(time.time() * 1000))
        query_string = ""
        if params:
            query_string = urlencode(params)
            url += "?" + query_string

        headers = {'Content-Type': 'application/json'}

        if not skip_auth:
            # Формируем строку для подписи: базовый путь + endpoint + (если GET – query string)
            parsed_url = urlparse(self.base_url)
            base_path = parsed_url.path  # например, "/api/mix/v1"
            request_path = base_path + endpoint
            if method.upper() == "GET" and query_string:
                request_path += "?" + query_string

            signature = self._generate_signature(timestamp, method, request_path, data)
            headers.update({
                'ACCESS-KEY': self.api_key,
                'ACCESS-SIGN': signature,
                'ACCESS-TIMESTAMP': timestamp,
                'ACCESS-PASSPHRASE': self.passphrase
            })

        if self.debug:
            print(f"\nDEBUG: Request: {method} {url}")
            print(f"DEBUG: Timestamp: {timestamp}")
            print("DEBUG: Headers:")
            for key, value in headers.items():
                if key == 'ACCESS-PASSPHRASE':
                    masked = value[:3] + '*' * (len(value) - 3)
                    print(f"  {key}: {masked}")
                else:
                    print(f"  {key}: {value}")
            if data:
                print(f"DEBUG: Data: {json.dumps(data)}")

        response = self.session.request(method=method, url=url, headers=headers, json=data)
        if self.debug:
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response body: {response.text[:2000]}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API request failed: {response.text}")

    def get_account_info(self, product_type="umcbl"):
        """
        Получает информацию о состоянии фьючерсного счёта.
        Обычно используется эндпоинт /account/accounts с параметром productType.

        :param product_type: Тип продукта (например, "umcbl" для USDT‑фьючерсов)
        :return: JSON с информацией о счёте
        """
        endpoint = "/account/accounts"
        params = {"productType": product_type}
        return self._request("GET", endpoint, params=params)
