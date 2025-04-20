# src/fetch_shorts.py
# Модуль для поиска и сбора Shorts с YouTube.

import requests
from src.config import YOUTUBE_API_KEY, FETCH_LIMIT

def search_shorts(query: str, limit: int = FETCH_LIMIT) -> list:
    """
    Ищет YouTube Shorts по заданному запросу.

    Args:
        query: Поисковый запрос.
        limit: Максимальное количество результатов.

    Returns:
        Список словарей с информацией о найденных Shorts (видео ID, название и т.д.).
        Возвращает пустой список в случае ошибки или отсутствия результатов.
    """
    print(f"Searching for Shorts with query: '{query}'")
    shorts_list = []
    # TODO: Реализовать логику поиска Shorts через YouTube Data API.
    # Учитывайте, что API может не иметь прямого фильтра "Shorts".
    # Возможно, придется искать обычные видео и проверять их длительность или другие признаки.
    # Пример API запроса:
    # url = "https://www.googleapis.com/youtube/v3/search"
    # params = {
    #     "key": YOUTUBE_API_KEY,
    #     "q": query,
    #     "part": "snippet",
    #     "maxResults": limit,
    #     "type": "video"
    #     # Возможно, добавить фильтр по длительности, если API поддерживает (не для search endpoint)
    # }
    # try:
    #     response = requests.get(url, params=params)
    #     response.raise_for_status() # Поднимет исключение для плохих статусов (4xx или 5xx)
    #     data = response.json()
    #     for item in data.get("items", []):
    #         video_id = item['id']['videoId']
    #         title = item['snippet']['title']
    #         # Дополнительная проверка, действительно ли это Short (может потребоваться отдельный запрос к videos endpoint)
    #         shorts_list.append({"video_id": video_id, "title": title, "url": f"https://www.youtube.com/shorts/{video_id}"})
    #         if len(shorts_list) >= limit:
    #             break
    # except requests.exceptions.RequestException as e:
    #     print(f"Error fetching Shorts: {e}")
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")


    # Заглушка для примера
    print("Using placeholder Shorts data.")
    shorts_list = [
        {"video_id": "example_id_1", "title": "Placeholder Short 1", "url": "https://www.youtube.com/watch?v=example_id_1"},
        {"video_id": "example_id_2", "title": "Placeholder Short 2", "url": "https://www.youtube.com/watch?v=example_id_2"},
    ] # TODO: Удалить заглушку

    print(f"Found {len(shorts_list)} potential Shorts.")
    return shorts_list

if __name__ == "__main__":
    # Пример использования
    shorts = search_shorts("funny cats shorts")
    for short in shorts:
        print(f"ID: {short['video_id']}, Title: {short['title']}, URL: {short['url']}")