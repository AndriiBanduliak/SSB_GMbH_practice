-- Создаем базу данных, если она не существует
CREATE DATABASE IF NOT EXISTS crm_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Используем созданную базу данных
USE crm_db;

-- Создаем таблицу пользователей
-- В реальном проекте пароль должен храниться в виде хеша!
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL, -- Здесь будет храниться хеш пароля
    language VARCHAR(5) DEFAULT 'en',    -- 'en', 'de', 'ru'
    theme VARCHAR(10) DEFAULT 'light',   -- 'light', 'dark'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Можно добавить тестового пользователя (пароль 'password', нужно хешировать при регистрации)
-- INSERT INTO users (username, email, password_hash, language, theme) VALUES
-- ('testuser', 'test@example.com', 'hashed_password_here', 'en', 'light');

-- Добавьте другие таблицы по мере необходимости (clients, trades, etc.)
-- CREATE TABLE IF NOT EXISTS clients (...);
-- CREATE TABLE IF NOT EXISTS trades (...);
