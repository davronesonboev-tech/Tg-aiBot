-- SQL скрипт для создания таблиц в PostgreSQL
-- Выполните этот скрипт в Railway Database -> Query
-- Версия: 1.2 | Дата: 2025-09-08

-- ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ ДЛЯ ОБНОВЛЕНИЯ СУЩЕСТВУЮЩЕЙ БАЗЫ:
-- Выполните эти команды в Railway Database -> Query ПЕРЕД созданием таблиц
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_rps_games INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_quiz_games INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_weather_requests INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_banned BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_image_analyses INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_voice_messages INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_documents_processed INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_guess_games INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_magic_ball_questions INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS avg_response_time FLOAT DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_session_time INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS favorite_persona VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS preferred_language VARCHAR(10) DEFAULT 'ru';
ALTER TABLE users ADD COLUMN IF NOT EXISTS user_preferences JSONB;
ALTER TABLE users ADD COLUMN IF NOT EXISTS interaction_patterns JSONB;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_message_at TIMESTAMP;
ALTER TABLE message_logs ADD COLUMN IF NOT EXISTS tokens_used INTEGER;
ALTER TABLE message_logs ADD COLUMN IF NOT EXISTS model_used VARCHAR(50);
ALTER TABLE message_logs ADD COLUMN IF NOT EXISTS success BOOLEAN DEFAULT TRUE;
ALTER TABLE message_logs ADD COLUMN IF NOT EXISTS error_message TEXT;
ALTER TABLE message_logs ADD COLUMN IF NOT EXISTS context_length INTEGER;
ALTER TABLE message_logs ADD COLUMN IF NOT EXISTS message_metadata JSONB;
ALTER TABLE message_logs ADD COLUMN IF NOT EXISTS user_satisfaction INTEGER;

-- Команды для добавления недостающих колонок (выполнить отдельно если таблица уже существует)
DO $$
BEGIN
    -- Добавляем колонки в таблицу users, если они не существуют
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'total_rps_games') THEN
        ALTER TABLE users ADD COLUMN total_rps_games INTEGER DEFAULT 0;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'total_quiz_games') THEN
        ALTER TABLE users ADD COLUMN total_quiz_games INTEGER DEFAULT 0;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'total_weather_requests') THEN
        ALTER TABLE users ADD COLUMN total_weather_requests INTEGER DEFAULT 0;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'is_banned') THEN
        ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT FALSE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'total_image_analyses') THEN
        ALTER TABLE users ADD COLUMN total_image_analyses INTEGER DEFAULT 0;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'total_voice_messages') THEN
        ALTER TABLE users ADD COLUMN total_voice_messages INTEGER DEFAULT 0;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'total_documents_processed') THEN
        ALTER TABLE users ADD COLUMN total_documents_processed INTEGER DEFAULT 0;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'total_guess_games') THEN
        ALTER TABLE users ADD COLUMN total_guess_games INTEGER DEFAULT 0;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'total_magic_ball_questions') THEN
        ALTER TABLE users ADD COLUMN total_magic_ball_questions INTEGER DEFAULT 0;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'avg_response_time') THEN
        ALTER TABLE users ADD COLUMN avg_response_time FLOAT DEFAULT 0;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'total_session_time') THEN
        ALTER TABLE users ADD COLUMN total_session_time INTEGER DEFAULT 0;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'favorite_persona') THEN
        ALTER TABLE users ADD COLUMN favorite_persona VARCHAR(100);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'preferred_language') THEN
        ALTER TABLE users ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'ru';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'user_preferences') THEN
        ALTER TABLE users ADD COLUMN user_preferences JSONB;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'interaction_patterns') THEN
        ALTER TABLE users ADD COLUMN interaction_patterns JSONB;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'last_message_at') THEN
        ALTER TABLE users ADD COLUMN last_message_at TIMESTAMP;
    END IF;

    -- Добавляем колонки в таблицу message_logs, если они не существуют
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'message_logs' AND column_name = 'tokens_used') THEN
        ALTER TABLE message_logs ADD COLUMN tokens_used INTEGER;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'message_logs' AND column_name = 'model_used') THEN
        ALTER TABLE message_logs ADD COLUMN model_used VARCHAR(50);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'message_logs' AND column_name = 'success') THEN
        ALTER TABLE message_logs ADD COLUMN success BOOLEAN DEFAULT TRUE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'message_logs' AND column_name = 'error_message') THEN
        ALTER TABLE message_logs ADD COLUMN error_message TEXT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'message_logs' AND column_name = 'context_length') THEN
        ALTER TABLE message_logs ADD COLUMN context_length INTEGER;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'message_logs' AND column_name = 'message_metadata') THEN
        ALTER TABLE message_logs ADD COLUMN message_metadata JSONB;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'message_logs' AND column_name = 'user_satisfaction') THEN
        ALTER TABLE message_logs ADD COLUMN user_satisfaction INTEGER;
    END IF;
END $$;

-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language_code VARCHAR(10),
    is_premium BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    is_banned BOOLEAN DEFAULT FALSE,
    total_messages INTEGER DEFAULT 0,
    total_games INTEGER DEFAULT 0,
    total_facts INTEGER DEFAULT 0,
    total_jokes INTEGER DEFAULT 0,
    total_quotes INTEGER DEFAULT 0,
    total_calculations INTEGER DEFAULT 0,
    total_translations INTEGER DEFAULT 0,
    total_rps_games INTEGER DEFAULT 0,
    total_quiz_games INTEGER DEFAULT 0,
    total_weather_requests INTEGER DEFAULT 0,
    total_image_analyses INTEGER DEFAULT 0,
    total_voice_messages INTEGER DEFAULT 0,
    total_documents_processed INTEGER DEFAULT 0,
    total_guess_games INTEGER DEFAULT 0,
    total_magic_ball_questions INTEGER DEFAULT 0,
    total_quiz_correct INTEGER DEFAULT 0,
    total_quiz_hints INTEGER DEFAULT 0,
    avg_response_time FLOAT DEFAULT 0,
    total_session_time INTEGER DEFAULT 0,
    favorite_persona VARCHAR(100),
    preferred_language VARCHAR(10) DEFAULT 'ru',
    user_preferences JSONB,
    interaction_patterns JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP,
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
    processing_time FLOAT,
    tokens_used INTEGER,
    model_used VARCHAR(50),
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    context_length INTEGER,
    message_metadata JSONB,
    user_satisfaction INTEGER
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
