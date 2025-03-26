# services/kucoin/app.py
from fastapi import FastAPI, HTTPException
import os
import logging
#from kucoin.client import Client  # Исправленный импорт
from kucoin.client import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/get_balance")
def get_balance(token: str = None):
    # Получаем ключи из переменных окружения
    api_key = os.getenv("KUCOIN_API_KEY")
    secret_key = os.getenv("KUCOIN_SECRET_KEY")
    passphrase = os.getenv("KUCOIN_API_PASSPHRASE")
    if not api_key or not secret_key or not passphrase:
        logger.error("Kucoin API keys or passphrase are not set")
        raise HTTPException(
            status_code=500, detail="Missing Kucoin API credentials")
    try:
        # Создаем клиента Kucoin
        client = Client(api_key, secret_key, passphrase)
        # Пример запроса баланса (метод может отличаться, см. документацию)
        accounts = client.get_accounts()
        # Отфильтровываем аккаунты с ненулевым балансом
        result = [
            {"currency": acc.get("currency"), "balance": acc.get("balance")}
            for acc in accounts if float(acc.get("balance", 0)) > 0
        ]
        return result
    except Exception as e:
        logger.error(f"Error fetching Kucoin balance: {e}")
        raise HTTPException(status_code=500, detail=f"Kucoin API error: {e}")
