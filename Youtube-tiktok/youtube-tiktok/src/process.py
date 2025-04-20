# src/process.py
# Модуль для обработки видео с использованием ffmpeg.

import ffmpeg
import os
from src.config import DOWNLOAD_DIR, PROCESSED_DIR, MAX_SHORT_DURATION_SEC

def process_video(input_path: str, output_id: str) -> str | None:
    """
    Обрабатывает видеофайл (например, обрезка, изменение разрешения) для TikTok.

    Args:
        input_path: Полный путь к исходному видеофайлу.
        output_id: ID для формирования имени выходного файла.

    Returns:
        Полный путь к обработанному видеофайлу в случае успеха,
        или None в случае ошибки.
    """
    output_filename = f"{output_id}_processed.mp4"
    output_path = os.path.join(PROCESSED_DIR, output_filename)

    # TODO: Реализовать логику обработки видео с ffmpeg.
    # Это может включать:
    # 1. Обрезку видео до MAX_SHORT_DURATION_SEC, если оно длиннее.
    # 2. Изменение разрешения/соотношения сторон (TikTok обычно 9:16 вертикальное).
    # 3. Добавление водяных знаков (по желанию).
    # 4. Перекодирование в подходящий формат (например, h264).

    print(f"Processing video: {input_path} -> {output_path}")

    try:
        # Пример базовой обработки: простое копирование или перекодирование
        # Проверка длительности (требует анализа видео)
        probe = ffmpeg.probe(input_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        duration = float(video_info.get('duration', 0))

        print(f"Original duration: {duration:.2f} seconds")

        stream = ffmpeg.input(input_path)

        # Если видео длиннее, обрезаем
        if duration > MAX_SHORT_DURATION_SEC:
            print(f"Video is longer than {MAX_SHORT_DURATION_SEC}s. Trimming...")
            # Обрезка до MAX_SHORT_DURATION_SEC с начала
            stream = stream.trim(duration=MAX_SHORT_DURATION_SEC).setpts('PTS-STARTPTS')

        # Пример изменения размера/соотношения сторон (осторожно, может обрезать контент)
        # Для TikTok часто нужно 1080x1920 (9:16)
        # filter_complex = [
        #     # Center crop or add black bars if needed
        #     f'scale=ih*9/16:ih,pad=iw:ih*16/9:(ow-iw)/2:(oh-ih)/2' # Example: scale to 9:16 width, then pad vertically
        # ]
        # stream = stream.filter_complex(filter_complex)

        # Выполняем процесс
        stream = stream.output(output_path, vcodec='libx264', acodec='aac', strict='experimental')
        ffmpeg.run(stream, overwrite_output=True)

        print(f"Successfully processed video to: {output_path}")
        return output_path

    except ffmpeg.Error as e:
        print(f"FFmpeg error processing {input_path}: {e.stderr.decode()}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during video processing: {e}")
        return None

if __name__ == "__main__":
    # Пример использования
    # Для теста нужно иметь файл в директории DOWNLOAD_DIR
    # Предположим, у нас есть файл "test_video.mp4" в downloads/
    # Создайте пустой файл или скопируйте небольшой видеофайл для теста
    test_input_path = os.path.join(DOWNLOAD_DIR, "test_video.mp4")
    test_output_id = "test_processed"

    # Создайте заглушку файла для теста, если его нет
    if not os.path.exists(test_input_path):
        print(f"Creating a placeholder file for test: {test_input_path}")
        # WARNING: ffprobe/ffmpeg может не работать с абсолютно пустым файлом.
        # Лучше использовать реальный, даже очень короткий, видеофайл.
        # Альтернативно, можно пропустить этот if __name__ == "__main__": блок,
        # пока не будет реального скачанного файла.
        # open(test_input_path, 'a').close() # Это создаст пустой файл

        # Пример создания тестового видео с помощью ffmpeg (требует ffmpeg в PATH)
        try:
            print("Attempting to create a dummy video file for processing test...")
            dummy_output = os.path.join(DOWNLOAD_DIR, "test_video.mp4")
            (
                ffmpeg
                .input('color=c=blue:s=640x480:d=10', f='lavfi') # Синий экран 10 секунд
                .output(dummy_output, vcodec='libx264', pix_fmt='yuv420p')
                .run(overwrite_output=True, quiet=True)
            )
            test_input_path = dummy_output
            print(f"Dummy video created at {test_input_path}")
        except Exception as e:
            print(f"Could not create dummy video: {e}. Skipping processing test.")
            test_input_path = None # Отключаем тест, если не удалось создать файл


    if test_input_path and os.path.exists(test_input_path):
        processed_path = process_video(test_input_path, test_output_id)

        if processed_path:
            print(f"\nSuccessfully processed video to: {processed_path}")
            # Добавьте удаление тестовых файлов, если нужно
            # try:
            #     os.remove(test_input_path)
            #     os.remove(processed_path)
            #     print("Removed test files.")
            # except OSError as e:
            #     print(f"Error removing test files: {e}")
        else:
            print(f"\nFailed to process video: {test_input_path}")
    else:
        print("\nSkipping processing test as input file does not exist.")