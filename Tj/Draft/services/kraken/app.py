# services/kraken/app.py
from fastapi import FastAPI, HTTPException
import krakenex
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/get_balance")
def get_balance(token: str = None):
    # Получаем API ключи из переменных окружения
    api_key = os.getenv("KRAKEN_API_KEY")
    secret_key = os.getenv("KRAKEN_SECRET_KEY")
    if not api_key or not secret_key:
        logger.error("API ключи Kraken не установлены")
        raise HTTPException(
            status_code=500, detail="Отсутствуют API ключи Kraken")
    try:
        k = krakenex.API()
        k.load_key(api_key, secret_key)
        balance = k.query_private('Balance')
        return balance
    except Exception as e:
        logger.error(f"Ошибка получения баланса Kraken: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка API Kraken: {e}")
