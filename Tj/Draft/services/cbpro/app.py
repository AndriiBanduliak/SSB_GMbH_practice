from fastapi import FastAPI, HTTPException
from typing import Optional
import os, logging
import cbpro  # pip install cbpro
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI()

@app.get("/get_balance")
def get_balance(
    token: Optional[str] = None,
    api_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    passphrase: Optional[str] = None
):
    """
    Пример эндпоинта для получения баланса Coinbase Pro.
    Если api_key/secret_key/passphrase не переданы, берем их из переменных окружения.
    """
    if not api_key:
        api_key = os.getenv("CBPRO_API_KEY")
    if not secret_key:
        secret_key = os.getenv("CBPRO_SECRET_KEY")
    if not passphrase:
        passphrase = os.getenv("CBPRO_PASSPHRASE")

    if not api_key or not secret_key or not passphrase:
        logger.error("API ключи Coinbase Pro не установлены")
        raise HTTPException(status_code=500, detail="Отсутствуют API ключи Coinbase Pro")

    try:
        client = cbpro.AuthenticatedClient(api_key, secret_key, passphrase)
        accounts = client.get_accounts()  # Возвращает список аккаунтов
        # Для упрощения вернем словарь, в котором key = валюта, value = баланс
        balance_dict = {}
        for acc in accounts:
            currency = acc.get("currency")
            balance = acc.get("balance")
            if currency and balance and float(balance) > 0:
                balance_dict[currency] = balance
        return balance_dict
    except Exception as e:
        logger.error(f"Ошибка обращения к API Coinbase Pro: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка API Coinbase Pro: {e}")
