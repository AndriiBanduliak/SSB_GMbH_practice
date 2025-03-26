import time
import hashlib
import requests
import os
import logging
from fastapi import FastAPI, HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MEXCClient:
    def __init__(self, api_key, api_secret, debug=False, additional_offset=100):
        self.api_key = api_key.strip()
        self.api_secret = api_secret.strip()
        self.base_url = "https://www.mexc.com"
        self.debug = debug
        self.session = requests.Session()
        self.additional_offset = additional_offset

    def get_server_timestamp(self):
        endpoint = "/open/api/v2/common/timestamp"
        url = self.base_url + endpoint
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        server_time = int(data.get("data"))
        if self.debug:
            local_time = int(time.time() * 1000)
            offset = server_time - local_time
            logger.info(
                f"DEBUG: Server time: {server_time}, Local time: {local_time}, Offset: {offset}")
        return server_time

    def _generate_signature(self, params: dict):
        sorted_params = sorted(params.items())
        query_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        sign_str = query_string + self.api_secret
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
        return sign

    def get_account_info(self):
        endpoint = "/open/api/v2/account/info"
        url = self.base_url + endpoint
        # Получаем актуальное серверное время и добавляем небольшой оффсет (например, 100 мс)
        req_time = self.get_server_timestamp() + self.additional_offset
        params = {
            "api_key": self.api_key,
            "req_time": req_time
        }
        params["sign"] = self._generate_signature(params)
        if self.debug:
            logger.info(f"DEBUG: URL: {url}")
            logger.info(f"DEBUG: Params: {params}")
        response = self.session.get(url, params=params)
        if self.debug:
            logger.info(f"DEBUG: Response status: {response.status_code}")
            logger.info(f"DEBUG: Response body: {response.text}")
        response.raise_for_status()
        return response.json()


app = FastAPI(title="MEXC API Service")


@app.get("/get_balance")
def get_balance(token: str = None, api_key: str = None, secret_key: str = None):
    if not api_key:
        api_key = os.getenv("MEXC_API_KEY")
    if not secret_key:
        secret_key = os.getenv("MEXC_SECRET_KEY")

    if not api_key or not secret_key:
        logger.error("API ключи MEXC не установлены")
        raise HTTPException(
            status_code=500, detail="Отсутствуют API ключи MEXC")

    try:
        client = MEXCClient(api_key, secret_key,
                            debug=True, additional_offset=1000)
        account_info = client.get_account_info()
        return account_info
    except Exception as e:
        logger.error(f"Ошибка получения баланса MEXC: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка API MEXC: {e}")
