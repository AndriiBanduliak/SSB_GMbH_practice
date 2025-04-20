# src/download.py
# Модуль для загрузки видео с YouTube через yt-dlp.

import yt_dlp
import os
from src.config import DOWNLOAD_DIR

def download_video(video_url: str, video_id: str) -> str | None:
    """
    Загружает видео с YouTube по URL.

    Args:
        video_url: URL видео на YouTube.
        video_id: ID видео (используется для имени файла).

    Returns:
        Полный путь к загруженному файлу видео в случае успеха,
        или None в случае ошибки.
    """
    output_template = os.path.join(DOWNLOAD_DIR, f"{video_id}.%(ext)s")
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': output_template,
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True, # Уберите для более подробного вывода yt-dlp
        'no_warnings': True,
        'progress_hooks': [lambda d: print(f"Downloading {d['filename']} - {d['_percent_str']} {d['_eta_str']}") if d['status'] == 'downloading' else None],
        'postprocessor_hooks': [lambda d: print(f"Finished downloading {d['filename']}") if d['status'] == 'finished' else None],
    }

    try:
        print(f"Attempting to download video from URL: {video_url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            # yt-dlp может создавать файл без указанного расширения, затем переименовывать его
            # нужно найти реальный путь после загрузки
            # info_dict['requested_downloads'] содержит информацию о загруженных файлах
            downloaded_files = [f['filepath'] for f in info_dict.get('requested_downloads', [])]
            if downloaded_files:
                # Обычно загружается один файл (после слияния видео и аудио)
                final_filepath = downloaded_files[0]
                if os.path.exists(final_filepath):
                     print(f"Successfully downloaded to: {final_filepath}")
                     return final_filepath
                else:
                    print(f"Download finished, but expected file not found at {final_filepath}")
                    return None
            else:
                 print("yt-dlp finished, but no files were recorded as downloaded.")
                 return None

    except yt_dlp.DownloadError as e:
        print(f"Download failed for {video_url}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during download: {e}")
        return None

if __name__ == "__main__":
    # Пример использования (используйте реальный URL короткого видео для теста)
    # Найдите реальный Short URL, например: https://www.youtube.com/shorts/abcdefGHIjk
    # ВНИМАНИЕ: Загрузка контента может нарушать авторские права. Используйте только с разрешения владельца.
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Rick Roll - НЕ Short! Измените на реальный Short для теста
    test_id = "dQw4w9WgXcQ" # Пример ID

    print(f"NOTE: Using a non-Short URL '{test_url}' for demonstration. Replace with a real Short URL.")

    downloaded_path = download_video(test_url, test_id)

    if downloaded_path:
        print(f"\nSuccessfully downloaded video to: {downloaded_path}")
        # Добавьте удаление тестового файла, если нужно
        # try:
        #     os.remove(downloaded_path)
        #     print(f"Removed test file: {downloaded_path}")
        # except OSError as e:
        #     print(f"Error removing test file: {e}")
    else:
        print(f"\nFailed to download video from: {test_url}")