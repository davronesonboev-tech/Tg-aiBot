"""
Модуль с дополнительными утилитами и функциями для бота.
Включает калькулятор, переводчик, игры и другие полезные функции.
"""

import re
import random
import requests
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime

from logger import log_info, log_error
from gemini_client import gemini_client


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
        'uz': 'узбекский',
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
        Переводит текст на указанный язык с использованием Google Translate API.

        Args:
            text: Текст для перевода
            target_lang: Целевой язык (по умолчанию английский)

        Returns:
            str: Переведенный текст или None при ошибке
        """
        try:
            log_info(f"Перевод текста на {target_lang}: {text[:50]}...")

            # Проверяем, что язык поддерживается
            if target_lang not in self.SUPPORTED_LANGUAGES:
                return f"❌ Язык '{target_lang}' не поддерживается."

            # Для простоты используем Google Translate через бесплатный прокси
            # В продакшене лучше использовать официальный API
            translation = self._translate_with_google(text, target_lang)

            if translation:
                return translation
            else:
                # Fallback на mock-перевод
                return text

        except Exception as e:
            log_error(f"Ошибка при переводе текста: {str(e)}")
            return None

    def _translate_with_google(self, text: str, target_lang: str) -> Optional[str]:
        """
        Переводит текст через Google Translate API (бесплатный).

        Args:
            text: Текст для перевода
            target_lang: Целевой язык

        Returns:
            str: Переведенный текст или None
        """
        try:
            # Используем бесплатный Google Translate API
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'auto',  # Автоопределение исходного языка
                'tl': target_lang,  # Целевой язык
                'dt': 't',  # Тип возвращаемых данных
                'q': text
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Извлекаем переведенный текст из ответа
            if data and len(data) > 0 and len(data[0]) > 0:
                translated_text = ""
                for item in data[0]:
                    if item and len(item) > 0:
                        translated_text += item[0]

                if translated_text.strip():
                    return translated_text

            return None

        except requests.exceptions.RequestException as e:
            log_error(f"Ошибка сети при переводе: {str(e)}")
            return None
        except Exception as e:
            log_error(f"Ошибка при обработке перевода: {str(e)}")
            return None


class WeatherService:
    """Сервис для получения реальной информации о погоде через Open-Meteo API."""

    # Словарь с координатами основных городов Узбекистана
    CITY_COORDINATES = {
        "ташкент": (41.2995, 69.2401),
        "самарканд": (39.6542, 66.9597),
        "бухара": (39.7748, 64.4286),
        "андижан": (40.7833, 72.3333),
        "фергана": (40.3734, 71.7978),
        "намантан": (40.9983, 71.6726),
        "карши": (38.8352, 65.7842),
        "термез": (37.2242, 67.2783),
        "нукус": (42.4531, 59.6103),
        "ургенч": (41.5534, 60.6317),
        "навои": (40.0844, 65.3792),
        "гулистан": (40.4897, 68.7844),
        "чирчик": (41.4697, 69.5822),
        "джизак": (40.1158, 67.8422),
        "коканд": (40.5286, 70.9428),
        "ангрен": (41.0167, 70.1436),
        "алмалык": (40.8667, 69.6),
        "бекобод": (40.2208, 69.2697),
        "чиракчи": (41.4833, 69.55),
        "паркент": (41.3, 69.6833),
        "янгиюль": (41.1121, 69.0708),
        "кибрай": (41.3833, 69.45),
        "бука": (40.8, 69.1833),
        "бекабад": (40.2167, 69.2833),
        "зулфикар": (41.2167, 69.2167),
        "ташкентская область": (41.2995, 69.2401),  # По умолчанию Ташкент
        "каракалпакстан": (42.4531, 59.6103),  # Нукус
        "хорезм": (41.5534, 60.6317),  # Ургенч
        "кашкадарья": (38.8352, 65.7842),  # Карши
        "сурхандарья": (37.2242, 67.2783),  # Термез
        "сырдарья": (40.4897, 68.7844),  # Гулистан
        "наманган": (40.9983, 71.6726),  # Исправлено
        "джизак": (40.1158, 67.8422),
    }

    def get_weather(self, city: str) -> Optional[str]:
        """
        Получает реальную информацию о погоде для указанного города через Open-Meteo API.

        Args:
            city: Название города

        Returns:
            str: Информация о погоде или None при ошибке
        """
        try:
            log_info(f"Запрос реальной погоды для города: {city}")

            # Получаем координаты города
            coords = self._get_city_coordinates(city)
            if not coords:
                return f"❌ Город '{city}' не найден в базе данных.\n\nДоступные города: Ташкент, Самарканд, Бухара, Андижан, Фергана, Наманган, Карши, Термез, Нукус, Ургенч, Навои, Гулистан, Чирчик и другие."

            latitude, longitude = coords

            # Запрос к Open-Meteo API (бесплатный, без API ключа)
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": True,
                "hourly": "temperature_2m,relativehumidity_2m,windspeed_10m",
                "timezone": "Asia/Tashkent"
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Извлекаем текущую погоду
            current = data.get("current_weather", {})
            if not current:
                return f"❌ Не удалось получить данные о погоде для города {city}"

            temperature = current.get("temperature", "N/A")
            windspeed = current.get("windspeed", "N/A")
            winddirection = current.get("winddirection", "N/A")

            # Получаем влажность из почасовых данных
            hourly = data.get("hourly", {})
            humidity = "N/A"
            if hourly.get("relativehumidity_2m"):
                humidity = hourly["relativehumidity_2m"][0]

            # Определяем описание погоды по температуре и влажности
            weather_description = self._get_weather_description(temperature, humidity)

            # Определяем направление ветра
            wind_direction_text = self._get_wind_direction(winddirection)

            return f"🌤️ <b>Погода в {city.title()}</b>\n\n" \
                   f"🌡️ <b>Температура:</b> {temperature}°C\n" \
                   f"🌥️ <b>Состояние:</b> {weather_description}\n" \
                   f"💧 <b>Влажность:</b> {humidity}%\n" \
                   f"💨 <b>Ветер:</b> {windspeed} м/с {wind_direction_text}\n\n" \
                   f"<i>📊 Данные предоставлены Open-Meteo (бесплатно)</i>"

        except requests.exceptions.RequestException as e:
            log_error(f"Ошибка сети при запросе погоды для {city}: {str(e)}")
            return f"❌ Ошибка подключения к сервису погоды.\nПопробуйте позже."
        except Exception as e:
            log_error(f"Ошибка при получении погоды для {city}: {str(e)}")
            return f"❌ Не удалось получить погоду для города {city}."

    def _get_city_coordinates(self, city: str) -> Optional[Tuple[float, float]]:
        """
        Получает координаты города из словаря.

        Args:
            city: Название города

        Returns:
            Tuple[float, float]: (latitude, longitude) или None
        """
        city_lower = city.lower().strip()

        # Прямое совпадение
        if city_lower in self.CITY_COORDINATES:
            return self.CITY_COORDINATES[city_lower]

        # Поиск по частичному совпадению
        for city_name, coords in self.CITY_COORDINATES.items():
            if city_lower in city_name or city_name in city_lower:
                return coords

        return None

    def _get_weather_description(self, temperature: float, humidity: int) -> str:
        """
        Определяет описание погоды на основе температуры и влажности.

        Args:
            temperature: Температура в градусах Цельсия
            humidity: Влажность в процентах

        Returns:
            str: Описание погоды
        """
        if temperature >= 25:
            return "жарко, солнечно"
        elif temperature >= 15:
            return "тепло, комфортно"
        elif temperature >= 5:
            return "прохладно"
        elif temperature >= -5:
            return "холодно"
        else:
            return "очень холодно, мороз"

    def _get_wind_direction(self, degrees: float) -> str:
        """
        Преобразует направление ветра из градусов в текстовое описание.

        Args:
            degrees: Направление ветра в градусах

        Returns:
            str: Текстовое описание направления
        """
        if degrees is None:
            return ""

        directions = [
            "северный", "северо-восточный", "восточный", "юго-восточный",
            "южный", "юго-западный", "западный", "северо-западный"
        ]

        index = round(degrees / 45) % 8
        return directions[index]


class GameService:
    """Сервис для простых игр."""

    def play_rps(self, user_choice: str) -> str:
        """
        Игра камень-ножницы-бумага.

        Args:
            user_choice: Выбор пользователя (rock/scissors/paper или камень/ножницы/бумага)

        Returns:
            str: Результат игры
        """
        # Преобразование английских названий в русские
        choice_map = {
            'rock': 'камень',
            'scissors': 'ножницы',
            'paper': 'бумага'
        }

        # Если передан английский вариант, преобразуем
        if user_choice.lower() in choice_map:
            user_choice = choice_map[user_choice.lower()]

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
        Начинает игру угадай число с AI-генерированными подсказками.

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

        # Генерируем интересную подсказку через Gemini
        try:
            hint_prompt = f"Дай одну короткую и интересную подсказку или факт про число {number}. Максимум 2 предложения на русском языке."
            hint = gemini_client.generate_text_response(hint_prompt)
            if hint:
                hint = hint.strip()
                if len(hint) > 100:
                    hint = hint[:100] + "..."
            else:
                hint = "Это число имеет свою уникальную историю!"
        except Exception as e:
            print(f"Ошибка генерации подсказки для числа {number}: {e}")
            hint = "Попробуй угадать методом половинного деления!"

        difficulty_names = {
            'easy': 'Легкий',
            'medium': 'Средний',
            'hard': 'Сложный'
        }

        difficulty_name = difficulty_names.get(difficulty, 'Средний')

        message = f"🔢 <b>Игра: Угадай число!</b>\n\n🎯 Загадал число от {min_val} до {max_val}\n📊 Сложность: {difficulty_name}\n💡 <b>Подсказка:</b> {hint}\n\nПопробуй угадать! 🎲"

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

    def generate_quiz_question(self) -> Optional[Dict[str, Any]]:
        """
        Генерирует вопрос викторины с помощью Gemini AI.

        Returns:
            Dict с вопросом, вариантами ответов и правильным ответом или None при ошибке
        """
        try:
            prompt = """Создай один интересный вопрос викторины на русском языке по случайной теме (история, наука, география, искусство, спорт, кино и т.д.).

Требования:
1. Вопрос должен быть интересным и познавательным
2. Дай 4 варианта ответа (1, 2, 3, 4)
3. Только один правильный ответ
4. Укажи номер правильного ответа
5. Добавь небольшую подсказку или интересный факт

Формат ответа:
Вопрос: [вопрос]
1. [вариант 1]
2. [вариант 2]
3. [вариант 3]
4. [вариант 4]
Правильный ответ: [номер]
Подсказка: [краткая подсказка]"""

            response = gemini_client.generate_text_response(prompt)

            if response:
                # Парсим ответ Gemini
                lines = response.strip().split('\n')
                question = ""
                options = []
                correct_answer = ""
                hint = ""

                current_section = ""
                for line in lines:
                    line = line.strip()
                    if line.startswith('Вопрос:'):
                        question = line.replace('Вопрос:', '').strip()
                        current_section = "question"
                    elif line.startswith(('1.', '2.', '3.', '4.')):
                        option = line[3:].strip()
                        options.append(option)
                    elif line.startswith('Правильный ответ:'):
                        correct_answer = line.replace('Правильный ответ:', '').strip()
                    elif line.startswith('Подсказка:'):
                        hint = line.replace('Подсказка:', '').strip()

                if question and len(options) == 4 and correct_answer:
                    return {
                        'question': question,
                        'options': options,
                        'correct_answer': correct_answer,
                        'hint': hint if hint else "Подсказка недоступна"
                    }

        except Exception as e:
            print(f"Ошибка генерации вопроса викторины: {e}")

        return None

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

    def get_magic_ball_answer(self, user_question: str = "") -> str:
        """
        Возвращает креативный ответ волшебного шара через Gemini AI.

        Args:
            user_question: Вопрос пользователя (опционально для более персонализированного ответа)

        Returns:
            str: Креативный ответ волшебного шара
        """
        try:
            # Выбираем случайный стиль ответа
            styles = [
                "креативный и юмористический",
                "загадочный и мистический",
                "мотивирующий и позитивный",
                "философский и глубокий",
                "игривый и легкомысленный"
            ]

            style = random.choice(styles)

            if user_question and len(user_question.strip()) > 5:
                prompt = f"""Дай креативный ответ волшебного шара на вопрос: "{user_question.strip()[:100]}..."

Стиль ответа: {style}
Требования:
- Ответ должен быть кратким (1-2 предложения)
- Использовать эмодзи волшебного шара 🎱
- Быть оригинальным и интересным
- Не быть слишком предсказуемым
- На русском языке"""
            else:
                prompt = f"""Дай креативный ответ волшебного шара в стиле: {style}

Требования:
- Ответ должен быть кратким (1-2 предложения)
- Использовать эмодзи волшебного шара 🎱
- Быть оригинальным и интересным
- Не быть слишком предсказуемым
- На русском языке"""

            response = gemini_client.generate_text_response(prompt)

            if response and len(response.strip()) > 0:
                # Убираем лишние пробелы и кавычки
                answer = response.strip().strip('"').strip("'")

                # Ограничиваем длину ответа
                if len(answer) > 200:
                    answer = answer[:200] + "..."

                return f"🎱 {answer}"
            else:
                # Fallback на стандартные ответы
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

        except Exception as e:
            print(f"Ошибка генерации ответа волшебного шара: {e}")

            # Fallback на стандартные ответы при ошибке
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
        """Генерирует уникальный интересный факт с помощью ИИ из разных категорий."""
        try:
            # Выбираем случайную категорию для разнообразия
            categories = [
                "наука и открытия",
                "животные и природа",
                "космос и астрономия",
                "история и цивилизации",
                "технологии и изобретения",
                "человеческое тело",
                "океан и моря",
                "растения и экология",
                "погода и климат",
                "археология и древности"
            ]

            selected_category = random.choice(categories)

            prompt = f"""Придумай один уникальный и удивительный факт про {selected_category}.
            Факт должен быть:
            - Настоящим и научно обоснованным
            - Коротким (1-2 предложения)
            - Захватывающим и малоизвестным
            - На русском языке
            - Интересным для широкой аудитории

            Верни только сам факт без дополнительных комментариев, объяснений или ссылок."""

            fact = gemini_client.generate_text_response(prompt)

            if fact:
                # Убираем лишние пробелы и переносы строк
                fact = fact.strip()
                # Убираем кавычки если они есть
                fact = fact.strip('"\'')
                return f"🧠 <b>Интересный факт:</b>\n\n{fact}"
            else:
                # Fallback факты по категориям
                fallbacks = {
                    "наука и открытия": "🧬 ДНК была открыта в 1953 году, но до сих пор ученые изучают только 2% ее функций!",
                    "животные и природа": "🐘 Самый большой слон в истории весил целых 12 тонн!",
                    "космос и астрономия": "🌟 Звезды, которые мы видим ночью, могут уже не существовать!",
                    "история и цивилизации": "🏺 Древние римляне использовали мочу как отбеливатель для зубов!",
                    "технологии и изобретения": "💡 Первая компьютерная мышь была сделана из дерева в 1964 году!",
                }
                return f"🧠 <b>Интересный факт:</b>\n\n{random.choice(list(fallbacks.values()))}"

        except Exception as e:
            log_error(f"Ошибка генерации факта: {str(e)}")
            return "🧠 <b>Интересный факт:</b>\n\n🌍 Земля вращается быстрее, чем когда-либо в истории человечества!"

    def get_motivational_quote(self) -> str:
        """Генерирует уникальную мотивационную цитату с помощью ИИ из разных категорий."""
        try:
            # Выбираем случайную тему для разнообразия
            themes = [
                "успех и достижения",
                "настойчивость и преодоление трудностей",
                "мечты и цели",
                "саморазвитие и обучение",
                "работа и карьера",
                "отношения и дружба",
                "здоровье и спорт",
                "творчество и искусство",
                "время и жизнь",
                "счастье и позитив"
            ]

            selected_theme = random.choice(themes)

            prompt = f"""Создай одну оригинальную мотивационную цитату на русском языке про {selected_theme}.
            Цитата должна быть:
            - Короткой и запоминающейся (1-2 предложения)
            - Позитивной и вдохновляющей
            - Оригинальной (не копируй известные цитаты)
            - Свежей и современной

            Верни только саму цитату без кавычек, автора и дополнительных комментариев."""

            quote = gemini_client.generate_text_response(prompt)

            if quote:
                # Убираем лишние пробелы и переносы строк
                quote = quote.strip()
                # Убираем кавычки если они есть
                quote = quote.strip('"\'')
                return f"💭 <b>Мотивационная цитата:</b>\n\n«{quote}»"
            else:
                # Fallback цитаты по темам
                fallbacks = {
                    "успех и достижения": "«Успех - это не окончание, неудача - не фатальна: смелость продолжать - вот что важно!»",
                    "мечты и цели": "«Будущее принадлежит тем, кто верит в красоту своих мечтаний.»",
                    "настойчивость": "«Не бойся отказов. Каждый отказ - это шаг ближе к успеху.»",
                    "саморазвитие": "«Ваше время ограничено, не тратьте его на чужую жизнь.»",
                    "работа": "«Единственный способ сделать великую работу - любить то, что делаешь.»",
                }
                return f"💭 <b>Мотивационная цитата:</b>\n\n{random.choice(list(fallbacks.values()))}"

        except Exception as e:
            log_error(f"Ошибка генерации цитаты: {str(e)}")
            return "💭 <b>Мотивационная цитата:</b>\n\n«Каждый день - это новый шанс стать лучше.»"

    def get_random_joke(self) -> str:
        """Генерирует уникальную шутку с помощью ИИ с разнообразными темами."""
        try:
            # Выбираем случайную категорию для разнообразия
            categories = [
                "программирование и IT",
                "повседневная жизнь",
                "животные и природа",
                "еда и кулинария",
                "спорт и здоровье",
                "школа и образование",
                "семья и отношения",
                "путешествия",
                "техника и гаджеты",
                "искусство и творчество"
            ]

            selected_category = random.choice(categories)

            prompt = f"""Придумай одну оригинальную и смешную шутку на русском языке про {selected_category}.
            Шутка должна быть:
            - Короткой и понятной (1-3 предложения)
            - Без грубостей и обидных тем
            - Настоящей шуткой (с неожиданным punchline)
            - Свежей и оригинальной

            Формат: вопрос + ответ или просто смешная ситуация.

            Верни только саму шутку без дополнительных комментариев, кавычек или объяснений."""

            joke = gemini_client.generate_text_response(prompt)

            if joke:
                # Убираем лишние пробелы и переносы строк
                joke = joke.strip()
                # Убираем кавычки если они есть
                joke = joke.strip('"\'')
                return f"😂 <b>Шутка:</b>\n\n{joke}"
            else:
                # Fallback шутки по категориям
                fallbacks = {
                    "программирование и IT": "🤣 Почему программисты путают Хэллоуин и Рождество?\nПотому что Oct 31 = Dec 25!",
                    "повседневная жизнь": "😄 Почему зонт не идет в школу?\nПотому что он уже раскрыт!",
                    "животные и природа": "🐘 Почему слон не пользуется компьютером?\nОн боится мышки!",
                    "еда и кулинария": "🍕 Почему пицца никогда не бывает грустной?\nПотому что у нее много друзей сверху!",
                    "спорт и здоровье": "⚽ Почему футболисты всегда носят шорты?\nПотому что в длинных штанах не забьешь гол!",
                }
                return f"😂 <b>Шутка:</b>\n\n{random.choice(list(fallbacks.values()))}"

        except Exception as e:
            log_error(f"Ошибка генерации шутки: {str(e)}")
            return "😂 <b>Шутка:</b>\n\n😄 Что говорит программист жене?\n«У меня есть два предложения для тебя:\n1. Ты самая красивая.\n2. Установи обновление.»"


# Глобальные экземпляры сервисов
calculator = Calculator()
translator = Translator()
weather_service = WeatherService()
game_service = GameService()
fun_service = FunService()
