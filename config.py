"""
Модуль конфигурации бота.
Загружает переменные окружения и предоставляет доступ к настройкам.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


class Config:
    """Класс для хранения конфигурации бота."""

    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")

    # Google Gemini API Key
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")

    # Модель Gemini для использования
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "models/gemini-1.5-pro-002")

    # PostgreSQL Database URL
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

    # Админ ID
    ADMIN_USER_ID: int = int(os.getenv("ADMIN_USER_ID", "1395804259"))

    # URL для Gemini API
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1"

    # Максимальный размер файла для загрузки (в байтах) - 20MB
    MAX_FILE_SIZE: int = 20 * 1024 * 1024

    # Таймауты для запросов (в секундах)
    REQUEST_TIMEOUT: int = 30
    WHISPER_TIMEOUT: int = 60

    @classmethod
    def validate_config(cls) -> bool:
        """
        Проверяет наличие всех необходимых переменных окружения.

        Returns:
            bool: True если все переменные установлены, иначе False
        """
        required_vars = ["TELEGRAM_BOT_TOKEN", "GOOGLE_API_KEY", "DATABASE_URL"]
        missing_vars = []

        for var in required_vars:
            value = getattr(cls, var)
            if not value:
                missing_vars.append(var)

        if missing_vars:
            print(f"❌ Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")
            print("📝 Пожалуйста, заполните файл .env или установите переменные окружения")
            return False

        print("✅ Конфигурация загружена успешно")
        return True

    @classmethod
    def get_gemini_url(cls, model: str) -> str:
        """
        Получает URL для запроса к Gemini API.

        Args:
            model: Название модели Gemini

        Returns:
            str: Полный URL для API запроса
        """
        return f"{cls.GEMINI_BASE_URL}/{model}:generateContent"


# Создаем экземпляр конфигурации
config = Config()
