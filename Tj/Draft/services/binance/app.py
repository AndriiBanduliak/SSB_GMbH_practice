from fastapi import FastAPI, HTTPException
from typing import Optional
import os
import logging
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI()


@app.get("/get_balance")
def get_balance(
    token: Optional[str] = None,
    api_key: Optional[str] = None,
    secret_key: Optional[str] = None
):
    # Если в query не передали, то берем из переменных окружения
    if not api_key:
        api_key = os.getenv("BINANCE_API_KEY")
    if not secret_key:
        secret_key = os.getenv("BINANCE_SECRET_KEY")

    if not api_key or not secret_key:
        logger.error("API ключи Binance не установлены")
        raise HTTPException(
            status_code=500, detail="Отсутствуют API ключи Binance")

    try:
        client = Client(api_key, secret_key)
        account_info = client.get_account()
        # Собираем словарь вида {"balance": <число>} или что‑то подобное
        balances = {}
        for asset in account_info.get("balances", []):
            free_amt = float(asset["free"])
            locked_amt = float(asset["locked"])
            total = free_amt + locked_amt
            if total > 0:
                balances[asset["asset"]] = total
        return balances
    except (BinanceAPIException, BinanceRequestException) as e:
        logger.error(f"Ошибка обращения к API Binance: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка API Binance: {e}")