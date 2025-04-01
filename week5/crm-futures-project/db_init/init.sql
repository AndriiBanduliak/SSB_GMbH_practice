-- Создаем базу данных, если она не существует
-- Используем кодировку utf8mb4 для полной поддержки Unicode
CREATE DATABASE IF NOT EXISTS crm_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Используем созданную базу данных
USE crm_db;

-- Таблицу users и contacts будет создавать Flask-Migrate,
-- поэтому здесь оставляем этот файл МИНИМАЛЬНЫМ.
-- Он нужен только для создания самой базы данных (если она не существует).
-- Docker образ MySQL сам создаст пользователя и даст ему права на эту БД
-- на основе переменных окружения MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE.

-- Можно оставить комментарий для ясности
-- Таблицы 'users' и 'contacts' будут созданы миграциями Alembic (Flask-Migrate).

