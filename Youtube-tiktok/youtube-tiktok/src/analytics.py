# src/analytics.py
# Модуль для сбора аналитики и генерации отчётов.

import json
import os
from datetime import datetime
from src.config import ANALYTICS_DIR
# Возможно, потребуется интеграция с TikTok API для получения статистики (если доступно)

def record_publication(video_id: str, tiktok_post_url: str, metadata: dict):
    """
    Записывает информацию об успешной публикации.

    Args:
        video_id: ID исходного видео на YouTube.
        tiktok_post_url: URL опубликованного поста в TikTok.
        metadata: Метаданные видео, использованные для публикации.
    """
    print(f"Recording publication for {video_id} at {tiktok_post_url}")
    record = {
        "youtube_video_id": video_id,
        "tiktok_post_url": tiktok_post_url,
        "publication_timestamp": datetime.now().isoformat(),
        "metadata_used": metadata # Сохраняем метаданные, которые были использованы
        # Добавьте другие данные, которые могут быть полезны
    }

    filename = os.path.join(ANALYTICS_DIR, "publications.jsonl") # JSON Lines формат
    try:
        with open(filename, "a") as f:
            f.write(json.dumps(record) + "\n")
        print("Publication record saved.")
    except IOError as e:
        print(f"Error writing publication record to {filename}: {e}")

# TODO: Добавить функции для сбора аналитики из TikTok (если API доступно)
# def fetch_tiktok_analytics(post_url: str) -> dict:
#    """
#    Пытается получить аналитику для опубликованного поста.
#    """
#    print(f"Fetching analytics for {post_url}...")
#    # Реализация с использованием TikTok API или парсинга (не рекомендуется)
#    analytics_data = {
#        "views": 0,
#        "likes": 0,
#        "comments": 0,
#        "shares": 0,
#        "fetch_timestamp": datetime.now().isoformat()
#    }
#    # TODO: Заполнить реальными данными
#    print("Placeholder analytics fetched.")
#    return analytics_data

def generate_report():
    """
    Генерирует отчёт на основе собранных данных.
    """
    print("Generating analytics report...")
    publications_file = os.path.join(ANALYTICS_DIR, "publications.jsonl")
    all_records = []

    if not os.path.exists(publications_file):
        print("No publication records found.")
        return

    try:
        with open(publications_file, "r") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    all_records.append(record)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON line: {line.strip()}")

        if not all_records:
            print("No valid publication records found.")
            return

        # TODO: Обработать данные и сгенерировать отчет
        # Например:
        # - Количество опубликованных видео
        # - Список опубликованных видео
        # - (Если есть аналитика из TikTok) Среднее количество просмотров/лайков
        # - Видео с лучшими показателями

        print(f"Total publications recorded: {len(all_records)}")
        print("\nRecent Publications:")
        for record in all_records[-5:]: # Покажем последние 5
             pub_time = record.get("publication_timestamp", "N/A")
             yt_id = record.get("youtube_video_id", "N/A")
             tiktok_url = record.get("tiktok_post_url", "N/A")
             print(f"- [{pub_time}] YouTube: {yt_id}, TikTok: {tiktok_url}")

        # Пример сбора аналитики (если fetch_tiktok_analytics реализован)
        # print("\nFetching analytics for recent posts...")
        # for record in all_records[-3:]:
        #     tiktok_url = record.get("tiktok_post_url")
        #     if tiktok_url and tiktok_url != "N/A":
        #         analytics = fetch_tiktok_analytics(tiktok_url)
        #         print(f"  Post {tiktok_url}: Views={analytics.get('views', 'N/A')}, Likes={analytics.get('likes', 'N/A')}")


        report_filename = os.path.join(ANALYTICS_DIR, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(report_filename, "w") as f:
            f.write("TikTok Publication Report\n")
            f.write("="*30 + "\n\n")
            f.write(f"Generated on: {datetime.now().isoformat()}\n")
            f.write(f"Total publications recorded: {len(all_records)}\n\n")

            f.write("Recent Publications:\n")
            for record in all_records[-10:]:
                 pub_time = record.get("publication_timestamp", "N/A")
                 yt_id = record.get("youtube_video_id", "N/A")
                 tiktok_url = record.get("tiktok_post_url", "N/A")
                 f.write(f"- [{pub_time}] YouTube: {yt_id}, TikTok: {tiktok_url}\n")

            # TODO: Добавить более подробную аналитику в отчет


        print(f"\nReport generated: {report_filename}")

    except IOError as e:
        print(f"Error reading publication records from {publications_file}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during report generation: {e}")


if __name__ == "__main__":
    # Пример использования

    # Имитация записи нескольких публикаций
    print("Simulating recording publications...")
    record_publication("yt_id_001", "https://www.tiktok.com/@user/video/post_001", {"title": "Vid 1"})
    record_publication("yt_id_002", "https://www.tiktok.com/@user/video/post_002", {"title": "Vid 2"})
    record_publication("yt_id_003", "https://www.tiktok.com/@user/video/post_003", {"title": "Vid 3"})

    # Генерация отчета
    print("\nGenerating report...")
    generate_report()