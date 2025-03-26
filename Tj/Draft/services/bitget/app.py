from fastapi import FastAPI, HTTPException
from typing import Optional
import os
import logging
from dotenv import load_dotenv

# Импортируем BitgetFuturesClient из нашего пакета
from python_bitget.bitget_client import BitgetFuturesClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI(title="Bitget Futures API")


@app.get("/get_balance")
def get_balance(
    token: Optional[str] = None,
    api_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    passphrase: Optional[str] = None
):
    # Если параметры не переданы через запрос, берем их из переменных окружения
    if not api_key:
        api_key = os.getenv("BITGET_API_KEY")
    if not secret_key:
        secret_key = os.getenv("BITGET_SECRET_KEY")
    if not passphrase:
        passphrase = os.getenv("BITGET_PASSPHRASE")

    if not api_key or not secret_key or not passphrase:
        logger.error("API ключи Bitget или passphrase не установлены")
        raise HTTPException(
            status_code=500, detail="Отсутствуют API ключи Bitget или passphrase")

    try:
        # Создаем экземпляр клиента для фьючерсного API
        client = BitgetFuturesClient(
            api_key, secret_key, passphrase, debug=True)
        # Получаем информацию о счёте
        account_info = client.get_account_info(product_type="umcbl")

        # Предположим, что нужные данные лежат в account_info["data"]
        data = account_info.get("data", [])

        # Составляем список только с нужными полями
        filtered_data = []
        for item in data:
            filtered_data.append({
                "equity": item.get("equity"),
                "usdtEquity": item.get("usdtEquity"),
                "btcEquity": item.get("btcEquity"),
                "unrealizedPL": item.get("unrealizedPL"),
            })

        return filtered_data

    except Exception as e:
        logger.error(f"Ошибка обращения к API Bitget: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка API Bitget: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
