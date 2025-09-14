"""
Модуль с дополнительными утилитами и функциями для бота.
Включает калькулятор, переводчик, игры и другие полезные функции.
"""

import re
import random
import requests
from typing import Optional, Tuple, List
from datetime import datetime

from logger import log_info, log_error


class Calculator:
    """Простой калькулятор для математических выражений."""

    def evaluate_expression(self, expression: str) -> Optional[float]:
        """
        Вычисляет математическое выражение.

        Args:
            expression: Математическое выражение

        Returns:
            float: Результат вычисления или None при ошибке
        """
        try:
            # Очищаем выражение от потенциально опасных символов
            expression = re.sub(r'[^\d+\-*/().\s]', '', expression)

            # Заменяем математические операторы для безопасности
            expression = expression.replace('^', '**')

            # Вычисляем
            result = eval(expression, {"__builtins": {}})

            # Проверяем, что результат - число
            if isinstance(result, (int, float)):
                return float(result)

        except Exception as e:
            log_error(f"Ошибка при вычислении выражения '{expression}': {str(e)}")
            return None

        return None


class Translator:
    """Простой переводчик с использованием бесплатных API."""

    SUPPORTED_LANGUAGES = {
        'ru': 'русский',
        'en': 'английский',
        'es': 'испанский',
        'fr': 'французский',
        'de': 'немецкий',
        'it': 'итальянский',
        'pt': 'португальский',
        'zh': 'китайский',
        'ja': 'японский',
        'ko': 'корейский'
    }

    def translate_text(self, text: str, target_lang: str = 'en') -> Optional[str]:
        """
        Переводит текст на указанный язык.

        Args:
            text: Текст для перевода
            target_lang: Целевой язык (по умолчанию английский)

        Returns:
            str: Переведенный текст или None при ошибке
        """
        try:
            # Используем простой API для перевода (можно заменить на более надежный)
            # Для демонстрации используем mock-перевод
            log_info(f"Перевод текста на {target_lang}: {text[:50]}...")

            # В реальном приложении здесь был бы вызов API перевода
            # Например: Google Translate API, Yandex Translate API и т.д.

            # Пока возвращаем заглушку
            return f"[Перевод на {self.SUPPORTED_LANGUAGES.get(target_lang, target_lang)}]: {text}"

        except Exception as e:
            log_error(f"Ошибка при переводе текста: {str(e)}")
            return None


class WeatherService:
    """Сервис для получения информации о погоде."""

    def get_weather(self, city: str) -> Optional[str]:
        """
        Получает информацию о погоде для указанного города.

        Args:
            city: Название города

        Returns:
            str: Информация о погоде или None при ошибке
        """
        try:
            # В реальном приложении здесь был бы вызов Weather API
            # Например: OpenWeatherMap, WeatherAPI и т.д.

            log_info(f"Запрос погоды для города: {city}")

            # Mock-ответ для демонстрации
            weather_conditions = ["солнечно", "облачно", "дождь", "снег", "пасмурно"]
            temperatures = random.randint(-10, 35)

            return f"🌤️ Погода в {city.title()}:\n" \
                   f"🌡️ Температура: {temperatures}°C\n" \
                   f"🌥️ Состояние: {random.choice(weather_conditions)}\n" \
                   f"💨 Влажность: {random.randint(30, 90)}%\n" \
                   f"💨 Ветер: {random.randint(0, 20)} м/с"

        except Exception as e:
            log_error(f"Ошибка при получении погоды для {city}: {str(e)}")
            return None


class GameService:
    """Сервис для простых игр."""

    def play_rps(self, user_choice: str) -> str:
        """
        Игра камень-ножницы-бумага.

        Args:
            user_choice: Выбор пользователя (камень/ножницы/бумага)

        Returns:
            str: Результат игры
        """
        choices = ['камень', 'ножницы', 'бумага']
        user_choice = user_choice.lower().strip()

        if user_choice not in choices:
            return "❌ Выберите: камень, ножницы или бумага!"

        bot_choice = random.choice(choices)

        result = ""
        if user_choice == bot_choice:
            result = "🤝 Ничья!"
        elif (user_choice == 'камень' and bot_choice == 'ножницы') or \
             (user_choice == 'ножницы' and bot_choice == 'бумага') or \
             (user_choice == 'бумага' and bot_choice == 'камень'):
            result = "🎉 Ты победил!"
        else:
            result = "😢 Я победил!"

        return f"🤖 Я выбрал: {bot_choice}\n🧑 Ты выбрал: {user_choice}\n\n{result}"

    def guess_number_game(self, difficulty: str = 'medium') -> Tuple[str, int]:
        """
        Начинает игру угадай число.

        Args:
            difficulty: Сложность (easy/medium/hard)

        Returns:
            Tuple[str, int]: Сообщение и загаданное число
        """
        ranges = {
            'easy': (1, 10),
            'medium': (1, 100),
            'hard': (1, 1000)
        }

        min_val, max_val = ranges.get(difficulty, (1, 100))
        number = random.randint(min_val, max_val)

        message = f"🎮 Я загадал число от {min_val} до {max_val}!\n" \
                 f"Попробуй угадать! (сложность: {difficulty})"

        return message, number

    def check_guess(self, guess: int, target: int) -> str:
        """
        Проверяет угаданное число.

        Args:
            guess: Предполагаемое число
            target: Загаданное число

        Returns:
            str: Результат проверки
        """
        if guess < target:
            return "📈 Загаданное число больше! ⬆️"
        elif guess > target:
            return "📉 Загаданное число меньше! ⬇️"
        else:
            return "🎉 Правильно! Ты угадал! 🎊"

    def play_dice_game(self, bet: str = 'medium') -> str:
        """Игра в кости."""
        try:
            bets = {
                'low': (1, 3),
                'medium': (4, 10),
                'high': (11, 18)
            }

            min_bet, max_bet = bets.get(bet, (4, 10))
            user_dice = random.randint(min_bet, max_bet)
            bot_dice = random.randint(min_bet, max_bet)

            result = ""
            if user_dice > bot_dice:
                result = "🎉 Ты победил! 🎲"
            elif user_dice < bot_dice:
                result = "😢 Я победил! 🎲"
            else:
                result = "🤝 Ничья! 🎲"

            return f"🎯 <b>Игра в кости</b>\n\n" \
                   f"Твои кости: {user_dice}\n" \
                   f"Мои кости: {bot_dice}\n\n" \
                   f"{result}"
        except Exception as e:
            return f"❌ Ошибка в игре: {str(e)}"

    def get_random_question(self) -> str:
        """Возвращает случайный вопрос для викторины."""
        questions = [
            ("Какая планета ближе всего к Солнцу?", ["Меркурий", "Венера", "Земля", "Марс"]),
            ("Какой элемент имеет химический символ 'O'?", ["Кислород", "Золото", "Серебро", "Углерод"]),
            ("В каком году была основана компания Apple?", ["1976", "1980", "1970", "1985"]),
            ("Какая река самая длинная в мире?", ["Амазонка", "Нил", "Янцзы", "Миссисипи"]),
            ("Сколько континентов на Земле?", ["7", "6", "5", "8"]),
            ("Какой язык программирования самый популярный?", ["Python", "JavaScript", "Java", "C++"]),
            ("Какая страна самая большая по площади?", ["Россия", "Канада", "Китай", "США"]),
            ("Как называется спутник Земли?", ["Луна", "Ио", "Европа", "Ганимед"])
        ]

        question, options = random.choice(questions)
        options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])

        return f"🧠 <b>Викторина!</b>\n\n❓ {question}\n\n{options_text}\n\nОтветь номером правильного варианта!"

    def check_quiz_answer(self, question: str, user_answer: str, correct_answer: str) -> str:
        """Проверяет ответ на вопрос викторины."""
        try:
            answer_num = int(user_answer.strip())
            if 1 <= answer_num <= 4:
                if str(answer_num) == correct_answer:
                    return "🎉 Правильно! Ты умница! 🧠"
                else:
                    return "❌ Неправильно, но не расстраивайся! Попробуй еще раз."
            else:
                return "❌ Введи число от 1 до 4!"
        except ValueError:
            return "❌ Введи число от 1 до 4!"

    def get_magic_ball_answer(self) -> str:
        """Возвращает ответ волшебного шара."""
        answers = [
            "🎱 Определенно да!",
            "🎱 Без сомнения!",
            "🎱 Да, конечно!",
            "🎱 Скорее всего да",
            "🎱 Может быть...",
            "🎱 Трудно сказать",
            "🎱 Лучше не сейчас",
            "🎱 Вряд ли",
            "🎱 Нет, наверное",
            "🎱 Совсем нет!",
            "🎱 Никогда!",
            "🎱 Попробуй еще раз"
        ]
        return random.choice(answers)


class FunService:
    """Сервис для развлекательных функций."""

    def get_random_fact(self) -> str:
        """Возвращает случайный интересный факт."""
        facts = [
            "🐘 Самый большой слон весил 12 тонн!",
            "🦈 Акулы существовали за 200 миллионов лет до динозавров!",
            "🌍 Земля вращается быстрее, чем когда-либо в истории!",
            "🐝 Пчелы могут распознавать человеческие лица!",
            "🌟 Звезды, которые мы видим ночью, могут уже не существовать!",
            "🦒 Жирафы имеют такой же количество позвонков в шее, как и люди - 7!",
            "🌊 Океан содержит 99% всего жизненного пространства на Земле!",
            "🐙 Осьминоги имеют 3 сердца!",
            "🐧 Пингвины могут прыгать до 6 метров в высоту!",
            "🌳 Деревья общаются друг с другом через корни!"
        ]
        return f"🤓 Интересный факт:\n{random.choice(facts)}"

    def get_motivational_quote(self) -> str:
        """Возвращает мотивационную цитату."""
        quotes = [
            "💪 «Успех - это не окончание, неудача - не фатальна: смелость продолжать - вот что важно!»",
            "🚀 «Ваше время ограничено, не тратьте его на чужую жизнь.»",
            "🌟 «Единственный способ сделать великую работу - любить то, что делаешь.»",
            "💡 «Верь, что можешь, и ты уже на полпути.»",
            "🎯 «Будущее принадлежит тем, кто верит в красоту своих мечтаний.»",
            "🔥 «Не бойся отказов. Каждый отказ - это шаг ближе к успеху.»",
            "⚡ «Делай сегодня то, что другие не хотят, завтра живи так, как другие не могут.»",
            "🌈 «Каждый день - это новый шанс стать лучше.»",
            "💎 «Твой единственный предел - ты сам.»",
            "🎨 «Творчество - это умение соединять несоединимое.»"
        ]
        return random.choice(quotes)

    def get_random_joke(self) -> str:
        """Возвращает случайную шутку."""
        jokes = [
            "🤣 Почему программисты путают Хэллоуин и Рождество?\nПотому что Oct 31 = Dec 25!",
            "😄 Что говорит программист жене?\n«У меня есть два предложения для тебя:\n1. Ты самая красивая.\n2. Установи обновление.»",
            "😂 Почему JavaScript разработчики всегда носят очки?\nПотому что без них они ничего не видят!",
            "😆 Как называется самая тихая комната?\nБиблиотека. Ш-ш-ш!",
            "🤪 Почему курица перешла дорогу?\nЧтобы попасть на другую сторону!",
            "😜 Что общего между программистом и поэтом?\nОба работают с рифмами... код и стихи!",
            "🤭 Как называется самая быстрая машина?\nМерседес Бенц, конечно!",
            "😝 Почему компьютер пошел к врачу?\nУ него был вирус!",
            "🤗 Что говорит чайник программисту?\n«Завари-ка код!»",
            "😎 Почему программисты любят темные комнаты?\nПотому что там меньше багов!"
        ]
        return random.choice(jokes)


# Глобальные экземпляры сервисов
calculator = Calculator()
translator = Translator()
weather_service = WeatherService()
game_service = GameService()
fun_service = FunService()
