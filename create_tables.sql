-- SQL скрипт для создания таблиц в PostgreSQL
-- Выполните этот скрипт в Railway Database -> Query
-- Версия: 1.0 | Дата: 2025-09-08

-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language_code VARCHAR(10),
    is_premium BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    total_messages INTEGER DEFAULT 0,
    total_games INTEGER DEFAULT 0,
    total_facts INTEGER DEFAULT 0,
    total_jokes INTEGER DEFAULT 0,
    total_quotes INTEGER DEFAULT 0,
    total_calculations INTEGER DEFAULT 0,
    total_translations INTEGER DEFAULT 0,
    total_weather_requests INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    banned_until TIMESTAMP
);

-- Создание таблицы игровых сессий
CREATE TABLE IF NOT EXISTS game_sessions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    game_type VARCHAR(50),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    result VARCHAR(50),
    score INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    game_data JSONB
);

-- Создание таблицы логов сообщений
CREATE TABLE IF NOT EXISTS message_logs (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    message_type VARCHAR(50),
    content TEXT,
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_time FLOAT
);

-- Создание таблицы настроек пользователей
CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE REFERENCES users(id),
    current_persona VARCHAR(50) DEFAULT 'Дружелюбный помощник',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    language VARCHAR(10) DEFAULT 'ru',
    timezone VARCHAR(50) DEFAULT 'Asia/Tashkent',
    settings_data JSONB
);

-- Создание таблицы системной статистики
CREATE TABLE IF NOT EXISTS system_stats (
    id SERIAL PRIMARY KEY,
    stat_type VARCHAR(100) UNIQUE,
    value BIGINT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_game_sessions_user_id ON game_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_game_sessions_game_type ON game_sessions(game_type);
CREATE INDEX IF NOT EXISTS idx_message_logs_user_id ON message_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_message_logs_type ON message_logs(message_type);
CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active DESC);

-- Вставка начальной системной статистики
INSERT INTO system_stats (stat_type, value) VALUES
    ('total_users', 0),
    ('total_messages', 0),
    ('total_games', 0)
ON CONFLICT (stat_type) DO NOTHING;
