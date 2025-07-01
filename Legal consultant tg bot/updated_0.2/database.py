import sqlite3
from datetime import date
import logging
from typing import Tuple # Для аннотации типов возвращаемых значений

# Инициализируем логгер для этого модуля
# (Логирование настроено в `config.py` и импортировано в `main.py`)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Класс для управления взаимодействием с базой данных SQLite.
    Отвечает за подключение, создание таблиц, а также все CRUD-операции
    (Create, Read, Update, Delete) с данными пользователей, включая логику
    сброса дневных лимитов.

    Примечание: Для простых ботов SQLite с `check_same_thread=False` может быть приемлемым.
    Для высоконагруженных асинхронных приложений лучше рассмотреть `aiosqlite`
    или полноценные асинхронные ORM/базы данных.
    """
    def __init__(self, db_name: str):
        """
        Инициализирует менеджер базы данных и устанавливает соединение.
        :param db_name: Имя файла базы данных SQLite (например, 'multilang_bot.db').
        """
        # `check_same_thread=False` необходим, если вы используете одно соединение
        # к SQLite из разных потоков, что может быть в случае с telegram.ext.
        # Однако, более надежным является использование пула соединений
        # или aiosqlite для асинхронной работы.
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_table() # Убеждаемся, что таблица существует при инициализации
        logger.info(f"DatabaseManager initialized for DB: {db_name}")

    def _create_table(self):
        """
        Создает таблицу `users`, если она не существует.
        Эта таблица хранит данные пользователя и его статистику использования.
        """
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,           -- Уникальный идентификатор пользователя Telegram
                    username TEXT,                         -- Имя пользователя Telegram (если есть)
                    first_name TEXT,                       -- Имя пользователя Telegram
                    phone_number TEXT,                     -- Номер телефона пользователя (опционально)
                    questions_count INTEGER DEFAULT 0,     -- Счетчик вопросов к AI
                    documents_count INTEGER DEFAULT 0,     -- Счетчик обработанных документов
                    last_reset_date TEXT,                  -- Дата последнего сброса дневных лимитов (YYYY-MM-DD)
                    language_code TEXT DEFAULT 'uk'        -- Предпочитаемый язык пользователя
                )
            ''')
            self.conn.commit() # Сохраняем изменения в схеме базы данных
            logger.info("Users table checked/created successfully.")
        except sqlite3.Error as e:
            logger.critical(f"Failed to create users table: {e}")
            # В реальном приложении здесь можно поднять исключение или принять меры по восстановлению

    def get_or_create_user(self, user_id: int, username: str, first_name: str) -> Tuple[int, int, str]:
        """
        Извлекает данные пользователя из базы данных. Если пользователь не существует,
        создает новую запись. Ежедневно сбрасывает счетчики вопросов и документов.
        
        :param user_id: Уникальный ID пользователя Telegram.
        :param username: Имя пользователя Telegram (может быть None).
        :param first_name: Имя пользователя Telegram.
        :return: Кортеж из (questions_count, documents_count, language_code) для пользователя.
        """
        today_str = date.today().isoformat() # Получаем текущую дату в формате 'YYYY-MM-DD'
        
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = self.cursor.fetchone() # Пытаемся найти пользователя
        
        if user is None:
            # Пользователь новый, создаем запись
            self.cursor.execute(
                "INSERT INTO users (user_id, username, first_name, last_reset_date, language_code) VALUES (?, ?, ?, ?, ?)",
                (user_id, username, first_name, today_str, 'uk') # По умолчанию украинский язык
            )
            self.conn.commit()
            logger.info(f"New user created: {user_id} (username: {username})")
            return 0, 0, 'uk' # Для нового пользователя счетчики обнулены, язык по умолчанию
        
        # Пользователь существует, обновляем username и first_name на случай их изменения в Telegram
        self.cursor.execute("UPDATE users SET username = ?, first_name = ? WHERE user_id = ?", (username, first_name, user_id))
        self.conn.commit()
        
        # Разбираем полученные данные пользователя
        # user tuple indices: 0:user_id, 1:username, 2:first_name, 3:phone_number, 4:questions_count, 5:documents_count, 6:last_reset_date, 7:language_code
        q_count, d_count, last_reset, lang_code = user[4], user[5], user[6], user[7]
        
        # Если дата последнего сброса не соответствует текущей дате, сбрасываем счетчики
        if last_reset != today_str:
            self.cursor.execute("UPDATE users SET questions_count = 0, documents_count = 0, last_reset_date = ? WHERE user_id = ?", (today_str, user_id))
            self.conn.commit()
            logger.info(f"Daily limits reset for user {user_id} ({username}).")
            return 0, 0, lang_code # Возвращаем обнуленные счетчики
        
        # Если лимиты уже были сброшены сегодня, возвращаем текущие значения
        return q_count, d_count, lang_code

    def set_user_language(self, user_id: int, lang_code: str):
        """
        Устанавливает предпочитаемый язык для пользователя.
        :param user_id: ID пользователя.
        :param lang_code: Код языка (например, 'uk', 'en', 'de').
        """
        try:
            self.cursor.execute("UPDATE users SET language_code = ? WHERE user_id = ?", (lang_code, user_id))
            self.conn.commit()
            logger.info(f"User {user_id} language updated to '{lang_code}'.")
        except sqlite3.Error as e:
            logger.error(f"Failed to set language for user {user_id}: {e}")

    def set_user_phone(self, user_id: int, phone_number: str):
        """
        Сохраняет номер телефона пользователя.
        :param user_id: ID пользователя.
        :param phone_number: Номер телефона.
        """
        try:
            self.cursor.execute("UPDATE users SET phone_number = ? WHERE user_id = ?", (phone_number, user_id))
            self.conn.commit()
            logger.info(f"User {user_id} phone number updated: {phone_number}")
        except sqlite3.Error as e:
            logger.error(f"Failed to set phone number for user {user_id}: {e}")

    def increment_usage(self, user_id: int, usage_type: str):
        """
        Увеличивает счетчик использования для конкретного типа операции.
        :param user_id: ID пользователя.
        :param usage_type: Тип использования ('question' или 'document').
        """
        field = ""
        if usage_type == "question":
            field = "questions_count"
        elif usage_type == "document":
            field = "documents_count"
        else:
            logger.warning(f"Attempted to increment unknown usage type: {usage_type} for user {user_id}")
            return

        try:
            self.cursor.execute(f"UPDATE users SET {field} = {field} + 1 WHERE user_id = ?", (user_id,))
            self.conn.commit()
            logger.debug(f"User {user_id} incremented {usage_type} usage.")
        except sqlite3.Error as e:
            logger.error(f"Failed to increment {usage_type} for user {user_id}: {e}")

    def close(self):
        """
        Закрывает соединение с базой данных.
        Важно вызывать этот метод при завершении работы приложения
        для корректного сохранения всех данных и освобождения ресурсов.
        """
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")