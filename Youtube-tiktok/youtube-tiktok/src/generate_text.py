# src/generate_text.py
# Модуль для генерации заголовков и описаний для публикации в TikTok.

from typing import Dict, Any

def generate_caption(video_metadata: Dict[str, Any]) -> str:
    """
    Генерирует заголовок (caption) для видео на основе его метаданных.

    Args:
        video_metadata: Словарь с метаданными видео, полученными из metadata.py.

    Returns:
        Сгенерированный заголовок в виде строки.
    """
    print("Generating caption...")
    # TODO: Реализовать логику генерации заголовка.
    # Можно использовать:
    # - Название оригинального видео с YouTube.
    # - Ключевые слова из описания или тегов.
    # - Простые шаблоны.
    # - Более сложные методы с использованием NLP (spaCy, NLTK, Transformers).

    original_title = video_metadata.get("snippet", {}).get("title", "Cool Video")
    tags = video_metadata.get("snippet", {}).get("tags", [])

    # Простой шаблон
    caption = f"{original_title} #shorts #youtube #tiktokvideo"

    # Добавление некоторых тегов из оригинала (ограничить количество и длину)
    tiktok_tags = ["#" + tag.replace(" ", "") for tag in tags if len(tag) < 20][:5]
    caption += " " + " ".join(tiktok_tags)

    print(f"Generated caption: {caption}")
    return caption

def generate_description(video_metadata: Dict[str, Any]) -> str:
    """
    Генерирует описание для видео в TikTok.

    Args:
        video_metadata: Словарь с метаданными видео.

    Returns:
        Сгенерированное описание.
    """
    print("Generating description...")
    # TODO: Реализовать логику генерации описания.
    # Можно использовать:
    # - Описание оригинального видео (возможно, сокращенное).
    # - Призыв к действию (подпишись, лайкни).
    # - Ссылку на оригинал (если разрешено и возможно).

    original_description = video_metadata.get("snippet", {}).get("description", "")
    original_url = f"https://www.youtube.com/watch?v={video_metadata.get('id', 'unknown')}"

    # Простой шаблон описания
    description = f"Оригинальное видео: {original_url}\n\n"
    description += original_description[:200] + "..." if len(original_description) > 200 else original_description
    description += "\n\nЛайк и подписка!"

    print(f"Generated description (partial): {description[:100]}...") # Выводим часть для краткости
    return description

if __name__ == "__main__":
    # Пример использования
    # Нужны метаданные видео (используем заглушку из metadata.py)
    placeholder_metadata = {
        "id": "example_id_1",
        "snippet": {
            "title": "Awesome Cat Tricks Short 🐱",
            "description": "Watch my cat perform amazing tricks! #cat #shorts #animal",
            "tags": ["cat", "tricks", "funny", "animalshorts", "pets", "youtube", "viral"],
            "categoryId": "15"
        },
        "contentDetails": {"duration": "PT0M45S"},
        "statistics": {"viewCount": "5000", "likeCount": "500"}
    } # TODO: Использовать реальные метаданные для лучшего теста

    caption = generate_caption(placeholder_metadata)
    description = generate_description(placeholder_metadata)

    print("\n--- Generated Text ---")
    print(f"Caption: {caption}")
    print(f"Description:\n{description}")