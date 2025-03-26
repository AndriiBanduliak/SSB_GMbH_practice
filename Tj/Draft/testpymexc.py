from pymexc import futures
import time
import json

api_key = "mx0vgley1IlnB4RGnB"         # Замените на ваш API ключ для фьючерсов
api_secret = "91953a3f8bfb4eab9fe1f674af4c1a35"  # Замените на ваш секретный ключ

# Имя файла для сохранения сообщений
JSON_FILENAME = "messages.json"

def handle_message(message):
    """
    Обработчик входящих сообщений.
    Выводит сообщение в консоль и сохраняет его в JSON файл.
    Каждое сообщение сохраняется как отдельная строка.
    """
    print("Получено сообщение:", message)
    try:
        # Открываем файл в режиме добавления и записываем сообщение как JSON
        with open(JSON_FILENAME, "a", encoding="utf-8") as f:
            json.dump(message, f, ensure_ascii=False)
            f.write("\n")
    except Exception as e:
        print("Ошибка при записи в файл:", e)

# Инициализация HTTP клиента для фьючерсов
futures_client = futures.HTTP(api_key=api_key, api_secret=api_secret)

# Пример запроса: получаем индексную цену (например, для MX_USDT)
try:
    index_price = futures_client.index_price("MX_USDT")
    print("Индексная цена:", index_price)
except Exception as e:
    print("Ошибка при получении индексной цены:", e)

# Инициализация WebSocket клиента для фьючерсов с callback для личных данных
ws_futures_client = futures.WebSocket(
    api_key=api_key,
    api_secret=api_secret,
    personal_callback=handle_message  # Обработка личных уведомлений (если ключ имеет разрешения)
)

# Подписка на публичный стрим тикеров (маркет-данные)
ws_futures_client.tickers_stream(handle_message)

# Если требуется подписка на личный стрим (данные по аккаунту), можно раскомментировать:
# ws_futures_client.personal_stream(handle_message)

# Запуск бесконечного цикла для поддержания соединения WebSocket
while True:
    time.sleep(1)
