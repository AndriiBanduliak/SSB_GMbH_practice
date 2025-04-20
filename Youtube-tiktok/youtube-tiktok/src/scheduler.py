# src/scheduler.py
# Модуль для планирования задач публикации.

# Можно использовать библиотеки типа APScheduler, schedule или просто while цикл + time.sleep
# from apscheduler.schedulers.blocking import BlockingScheduler
import time
from datetime import datetime
from src.config import PUBLISH_INTERVAL_HOURS
# Импортируем функции из других модулей, которые будут выполняться по расписанию
from src.fetch_shorts import search_shorts
from src.metadata import get_video_metadata
from src.download import download_video
from src.process import process_video
from src.generate_text import generate_caption, generate_description
from src.publish import publish_to_tiktok

def run_publication_task(search_query: str = "youtube shorts"):
    """
    Выполняет полный цикл: поиск -> метаданные -> загрузка -> обработка -> публикация.
    """
    print(f"[{datetime.now()}] Running scheduled publication task...")

    # 1. Поиск Shorts
    shorts_candidates = search_shorts(search_query)

    if not shorts_candidates:
        print("No new Shorts candidates found. Skipping.")
        return

    # Возьмем первый найденный Short для обработки (можно доработать логику выбора)
    selected_short = shorts_candidates[0]
    video_id = selected_short.get("video_id")
    video_url = selected_short.get("url")

    if not video_id or not video_url:
        print("Invalid short data received. Skipping.")
        return

    print(f"Selected Short: ID={video_id}, URL={video_url}")

    # 2. Запрос метаданных
    metadata = get_video_metadata(video_id)
    if not metadata:
        print(f"Failed to get metadata for {video_id}. Skipping.")
        return

    # 3. Загрузка видео
    downloaded_path = download_video(video_url, video_id)
    if not downloaded_path:
        print(f"Failed to download video {video_id}. Skipping.")
        return

    # 4. Обработка видео
    processed_path = process_video(downloaded_path, video_id)
    # Optional: Удалить исходный загруженный файл после обработки
    # try:
    #     os.remove(downloaded_path)
    #     print(f"Removed original downloaded file: {downloaded_path}")
    # except OSError as e:
    #      print(f"Error removing original downloaded file {downloaded_path}: {e}")

    if not processed_path:
        print(f"Failed to process video {video_id}. Skipping.")
        return

    # 5. Генерация текста
    caption = generate_caption(metadata)
    description = generate_description(metadata) # TikTok использует только caption, но можно использовать description для дополнительной инфо

    # 6. Публикация в TikTok
    is_published = publish_to_tiktok(processed_path, caption, description)

    if is_published:
        print(f"Successfully published video {video_id} to TikTok.")
        # TODO: Записать в лог или базу данных информацию об успешной публикации
        # Optional: Удалить обработанный файл после публикации
        # try:
        #     os.remove(processed_path)
        #     print(f"Removed processed file: {processed_path}")
        # except OSError as e:
        #     print(f"Error removing processed file {processed_path}: {e}")
    else:
        print(f"Failed to publish video {video_id} to TikTok.")
        # TODO: Записать в лог информацию о неудачной публикации
        # TODO: Обработка ошибок (повтор, уведомление)

    print(f"[{datetime.now()}] Publication task finished.")


def start_scheduler(interval_hours: int = PUBLISH_INTERVAL_HOURS, initial_delay_seconds: int = 5):
    """
    Запускает планировщик для периодического выполнения задачи публикации.
    """
    print(f"Scheduler started. First run in {initial_delay_seconds} seconds, then every {interval_hours} hours.")

    # Использование простого цикла while для планирования
    time.sleep(initial_delay_seconds) # Начальная задержка перед первым запуском

    while True:
        try:
            run_publication_task()
        except Exception as e:
            print(f"An unexpected error occurred in the scheduled task: {e}")
            # Продолжаем цикл, чтобы планировщик не упал полностью

        print(f"Waiting for {interval_hours} hours until next run...")
        time.sleep(interval_hours * 3600) # Ждем интервал в секундах

    # --- Альтернативный вариант с APScheduler ---
    # scheduler = BlockingScheduler()
    # scheduler.add_job(run_publication_task, 'interval', hours=interval_hours)
    # print(f"Starting scheduler... Press Ctrl+C to exit.")
    # try:
    #     scheduler.start()
    # except (KeyboardInterrupt, SystemExit):
    #     pass
    # --------------------------------------------


if __name__ == "__main__":
    # Пример использования
    # Запустит задачу публикации сразу (после 5 секунд) и затем каждые PUBLISH_INTERVAL_HOURS
    start_scheduler()