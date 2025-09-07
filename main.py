#!/usr/bin/env python3
"""
Точка входа для Telegram AI бота.
Запускает бота и обрабатывает сигналы завершения.
"""

import asyncio
import signal
import sys
from typing import Optional

from config import config
from logger import logger, log_info, log_error
from database import init_database, get_db_manager
# Whisper больше не используется - все через Gemini API

# Импорт бота будет после инициализации БД
ai_bot = None


class BotRunner:
    """Класс для управления запуском и остановкой бота."""

    def __init__(self):
        """Инициализирует runner."""
        self.running = False
        self.task: Optional[asyncio.Task] = None

    async def start_bot(self):
        """Запускает бота."""
        global ai_bot

        try:
            log_info("Запуск Telegram AI бота...")

            # Импортируем и создаем бота после инициализации БД
            from bot import AIBot
            if ai_bot is None:
                ai_bot = AIBot()
                log_info("Бот успешно создан")

            self.running = True
            await ai_bot.start_polling()
        except Exception as e:
            log_error(f"Ошибка при запуске бота: {str(e)}", exc=e)
            raise
        finally:
            self.running = False

    async def stop_bot(self):
        """Останавливает бота."""
        global ai_bot

        log_info("Получен сигнал остановки бота")
        self.running = False

        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        if ai_bot:
            await ai_bot.stop()

    def signal_handler(self, signum, frame):
        """Обработчик сигналов системы."""
        log_info(f"Получен сигнал: {signum}")
        asyncio.create_task(self.stop_bot())

    async def run(self):
        """Основной метод запуска."""
        # Проверяем конфигурацию
        if not config.validate_config():
            log_error("Конфигурация не прошла валидацию. Завершение работы.")
            sys.exit(1)

        # Инициализируем базу данных
        if config.DATABASE_URL:
            try:
                log_info("Подключение к базе данных...")
                init_database(config.DATABASE_URL)

                # Проверяем подключение
                db_manager = get_db_manager()
                if db_manager:
                    log_info("База данных инициализирована успешно")
                else:
                    log_error("Не удалось получить менеджер базы данных")
                    sys.exit(1)

            except Exception as e:
                log_error(f"Ошибка инициализации базы данных: {str(e)}")
                log_error("Проверьте DATABASE_URL и доступность PostgreSQL сервера")
                sys.exit(1)
        else:
            log_error("DATABASE_URL не установлена в переменных окружения")
            log_error("Добавьте DATABASE_URL в Railway Variables")
            sys.exit(1)

        # Настраиваем обработчики сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # В Windows нет SIGHUP, поэтому проверяем
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, self.signal_handler)

        try:
            # Запускаем бота
            self.task = asyncio.create_task(self.start_bot())
            await self.task

        except KeyboardInterrupt:
            log_info("Получен KeyboardInterrupt")
            await self.stop_bot()
        except Exception as e:
            log_error(f"Неожиданная ошибка: {str(e)}", exc=e)
            await self.stop_bot()
            sys.exit(1)


def main():
    """Главная функция."""
    print("🤖 Telegram AI Bot")
    print("=" * 50)

    runner = BotRunner()

    try:
        asyncio.run(runner.run())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {str(e)}")
        sys.exit(1)

    print("✅ Бот завершил работу")


if __name__ == "__main__":
    main()
