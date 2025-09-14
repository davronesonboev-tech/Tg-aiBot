"""
Модуль логирования для бота.
Настраивает логирование в консоль и файл.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Создаем директорию для логов, если она не существует
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)


class BotLogger:
    """Класс для настройки логирования бота."""

    @staticmethod
    def setup_logger(
        name: str = "telegram_ai_bot",
        level: int = logging.INFO,
        log_to_file: bool = True,
        log_to_console: bool = True
    ) -> logging.Logger:
        """
        Настраивает и возвращает логгер.

        Args:
            name: Имя логгера
            level: Уровень логирования
            log_to_file: Логировать в файл
            log_to_console: Логировать в консоль

        Returns:
            logging.Logger: Настроенный логгер
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Очищаем существующие обработчики
        logger.handlers.clear()

        # Форматтер для сообщений
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Обработчик для консоли
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # Обработчик для файла
        if log_to_file:
            file_handler = logging.FileHandler(
                logs_dir / "bot.log",
                encoding='utf-8',
                mode='a'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger


# Создаем глобальный логгер для бота
logger = BotLogger.setup_logger()

# Функции для удобного логирования
def log_info(message: str, user_id: Optional[int] = None) -> None:
    """Логирует информационное сообщение."""
    if user_id:
        message = f"[User {user_id}] {message}"
    logger.info(message)


def log_error(message: str, user_id: Optional[int] = None, exc: Optional[Exception] = None) -> None:
    """Логирует сообщение об ошибке."""
    if user_id:
        message = f"[User {user_id}] {message}"
    if exc:
        logger.error(message, exc_info=exc)
    else:
        logger.error(message)


def log_warning(message: str, user_id: Optional[int] = None) -> None:
    """Логирует предупреждение."""
    if user_id:
        message = f"[User {user_id}] {message}"
    logger.warning(message)


def log_debug(message: str, user_id: Optional[int] = None) -> None:
    """Логирует отладочное сообщение."""
    if user_id:
        message = f"[User {user_id}] {message}"
    logger.debug(message)
