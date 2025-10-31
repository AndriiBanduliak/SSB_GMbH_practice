import logging
from openai import AsyncOpenAI, APIError # Импортируем классы для работы с OpenAI API и обработки ошибок
from config import Config, Translations # Импортируем нашу конфигурацию и переводы

# Инициализируем логгер для этого модуля
# (Настройка логирования происходит в config.py и вызывается в main.py)
logger = logging.getLogger(__name__)

class OpenAIService:
    """
    Класс для управления всеми взаимодействиями с OpenAI API.
    Предоставляет методы для отправки запросов к языковой модели
    и обработки возможных ошибок API.
    """
    def __init__(self, api_key: str):
        """
        Инициализирует клиент OpenAI.
        :param api_key: Ваш ключ API для OpenAI.
        """
        try:
            if not api_key:
                raise ValueError("OpenAI API key is required")
            # AsyncOpenAI - асинхронный клиент для неблокирующих операций
            self.client = AsyncOpenAI(api_key=api_key)
            logger.info("OpenAIService: OpenAI client initialized.")
        except Exception as e:
            logger.critical(f"Failed to initialize OpenAI client: {e}")
            raise

    async def get_ai_response(self, system_prompt_key: str, user_prompt: str, lang_code: str, document_content: str = "") -> str:
        """
        Отправляет запрос к языковой модели OpenAI (GPT-4o-mini).
        
        Формирует системный и пользовательский промпты, отправляет их в AI
        и возвращает сгенерированный ответ. Обрабатывает ошибки API.

        :param system_prompt_key: Ключ для получения системного промпта из `Translations`.
                                  Системный промпт определяет роль AI.
        :param user_prompt: Текст вопроса или инструкций от пользователя.
        :param lang_code: Код языка ('uk', 'en', 'de') для получения правильных переводов промптов.
        :param document_content: Опциональный текст документа, который нужно
                                 передать AI для анализа/редактирования.
                                 Предполагается, что он уже был обрезан до необходимой длины
                                 вызывающим методом (например, в handlers/ai_interaction.py).
        :return: Ответ AI в виде строки или сообщение об ошибке.
        """
        # Получаем имя языка для использования в системном промпте
        lang_name = Translations.LANGUAGES.get(lang_code, "English")
        
        # Получаем системный промпт из Translations, используя ключ и подставляя имя языка
        system_prompt = Translations.get_text(lang_code, system_prompt_key, lang_name=lang_name)
        
        # Формируем полный пользовательский промпт, добавляя содержимое документа, если оно есть
        # AI модель Config.OPENAI_MODEL имеет ограничение на контекст.
        # Длинные документы должны быть предварительно обработаны (сокращены) в `handle_document`.
        full_user_prompt = f"{user_prompt}\n\nDocument for processing:\n{document_content}" if document_content else user_prompt
        
        # Составляем список сообщений для API чата (роль "system" и "user")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user_prompt}
        ]
        
        try:
            # Отправляем запрос к OpenAI API с таймаутом
            import asyncio
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=Config.OPENAI_MODEL,  # Используем модель, определенную в конфигурации
                    messages=messages,
                    max_tokens=3500,            # Максимальное количество токенов в ответе AI
                    temperature=0.3             # Температура для контроля креативности (0.0-2.0, 0.3 - сбалансировано)
                ),
                timeout=60.0  # 60 секунд таймаут
            )
            
            # Извлекаем и возвращаем текст ответа от AI
            if response.choices and len(response.choices) > 0:
                ai_response_content = response.choices[0].message.content
                if ai_response_content:
                    logger.debug(f"OpenAIService: Successfully got AI response for user prompt: {user_prompt[:50]}...")
                    return ai_response_content
                else:
                    logger.warning("OpenAIService: Received empty response from AI")
                    return Translations.get_text(lang_code, "error_generic")
            else:
                logger.warning("OpenAIService: No choices in AI response")
                return Translations.get_text(lang_code, "error_generic")
            
        except asyncio.TimeoutError:
            logger.error("OpenAIService: Request to OpenAI API timed out")
            return Translations.get_text(lang_code, "error_generic")
            
        except APIError as e:
            # Обработка специфических ошибок OpenAI API (например, проблемы с аутентификацией, лимиты, неверный запрос)
            logger.error(f"OpenAIService: OpenAI API error occurred: Status Code {e.status_code}, Response: {e.response}")
            return Translations.get_text(lang_code, "error_generic") # Возвращаем общее сообщение об ошибке пользователю
            
        except Exception as e:
            # Обработка любых других неожиданных ошибок
            logger.error(f"OpenAIService: An unexpected error occurred in get_ai_response: {e}", exc_info=True)
            return Translations.get_text(lang_code, "error_generic")

# Единый экземпляр OpenAIService, который будет импортирован в другие модули.
# Это удобно, так как не нужно передавать объект сервиса через множество функций.
# Это паттерн "Singleton" (хотя и не строгий), где один экземпляр сервиса используется по всему приложению.
openai_service = OpenAIService(Config.OPENAI_API_KEY)