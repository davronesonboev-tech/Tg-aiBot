"""
Основной модуль Telegram бота с ИИ.
Обрабатывает текстовые сообщения, изображения и голосовые сообщения.
"""

import asyncio
from typing import Optional, Tuple

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command

from config import config
from logger import log_info, log_error, log_warning
from gemini_client import gemini_client
from personas import persona_manager, PersonaType
from utils import calculator, translator, weather_service, game_service, fun_service
from memory import memory_manager
from keyboards import keyboard_manager
from database import get_db_manager


class AIBot:
    """Основной класс Telegram бота с ИИ."""

    def __init__(self):
        """Инициализирует бота."""
        self.bot = Bot(
            token=config.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher()
        self.db = get_db_manager()

        # Регистрируем обработчики
        self._register_handlers()

    def _register_handlers(self):
        """Регистрирует все обработчики сообщений."""
        # Обработчик команды /start
        self.dp.message.register(self.cmd_start, Command("start"))

        # Обработчик команды /help
        self.dp.message.register(self.cmd_help, Command("help"))

        # Команды смены режимов
        self.dp.message.register(self.cmd_friendly, Command("friendly"))
        self.dp.message.register(self.cmd_friendly, Command("дружелюбный"))
        self.dp.message.register(self.cmd_programmer, Command("programmer"))
        self.dp.message.register(self.cmd_programmer, Command("программист"))
        self.dp.message.register(self.cmd_programmer, Command("code"))
        self.dp.message.register(self.cmd_programmer, Command("код"))
        self.dp.message.register(self.cmd_expert, Command("expert"))
        self.dp.message.register(self.cmd_expert, Command("эксперт"))
        self.dp.message.register(self.cmd_creative, Command("creative"))
        self.dp.message.register(self.cmd_creative, Command("креатив"))
        self.dp.message.register(self.cmd_creative, Command("идеи"))
        self.dp.message.register(self.cmd_professional, Command("professional"))
        self.dp.message.register(self.cmd_professional, Command("профессионал"))
        self.dp.message.register(self.cmd_professional, Command("бизнес"))
        self.dp.message.register(self.cmd_current_mode, Command("mode"))
        self.dp.message.register(self.cmd_current_mode, Command("режим"))

        # Команды дополнительных функций
        self.dp.message.register(self.cmd_calculate, Command("calc"))
        self.dp.message.register(self.cmd_calculate, Command("калькулятор"))
        self.dp.message.register(self.cmd_calculate, Command("calculate"))
        self.dp.message.register(self.cmd_game_rps, Command("rps"))
        self.dp.message.register(self.cmd_game_rps, Command("камень"))
        self.dp.message.register(self.cmd_game_guess, Command("guess"))
        self.dp.message.register(self.cmd_game_guess, Command("угадай"))
        self.dp.message.register(self.cmd_fun_fact, Command("fact"))
        self.dp.message.register(self.cmd_fun_fact, Command("факт"))
        self.dp.message.register(self.cmd_fun_quote, Command("quote"))
        self.dp.message.register(self.cmd_fun_quote, Command("цитата"))
        self.dp.message.register(self.cmd_fun_joke, Command("joke"))
        self.dp.message.register(self.cmd_fun_joke, Command("шутка"))

        # Новые игры и развлечения
        self.dp.message.register(self.cmd_game_dice, Command("dice"))
        self.dp.message.register(self.cmd_game_dice, Command("кости"))
        self.dp.message.register(self.cmd_game_quiz, Command("quiz"))
        self.dp.message.register(self.cmd_game_quiz, Command("викторина"))
        self.dp.message.register(self.cmd_magic_ball, Command("ball"))
        self.dp.message.register(self.cmd_magic_ball, Command("шар"))
        self.dp.message.register(self.cmd_magic_ball, Command("волшебный"))
        self.dp.message.register(self.cmd_memory_clear, Command("clear"))
        self.dp.message.register(self.cmd_memory_clear, Command("очистить"))
        self.dp.message.register(self.cmd_memory_stats, Command("stats"))
        self.dp.message.register(self.cmd_memory_stats, Command("статистика"))

        # Добавляем команду для меню
        self.dp.message.register(self.show_main_menu, Command("menu"))

        # Обработчик текстовых сообщений
        self.dp.message.register(self.handle_text_message, lambda msg: msg.text and not msg.text.startswith('/'))

        # Обработчик изображений
        self.dp.message.register(self.handle_photo_message, lambda msg: msg.photo)

        # Обработчик голосовых сообщений
        self.dp.message.register(self.handle_voice_message, lambda msg: msg.voice)

        # Обработчик аудио файлов
        self.dp.message.register(self.handle_audio_message, lambda msg: msg.audio)

        # Обработчик callback query для кнопок
        self.dp.callback_query.register(self.handle_callback)

    async def cmd_start(self, message: types.Message):
        """Обработчик команды /start."""
        user_id = message.from_user.id
        log_info("Получена команда /start", user_id)

        # Сохраняем/обновляем пользователя в БД
        try:
            user_data = {
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name,
                'language_code': message.from_user.language_code,
                'is_premium': message.from_user.is_premium or False
            }
            self.db.get_or_create_user(user_id, **user_data)
        except Exception as e:
            log_error(f"Ошибка сохранения пользователя {user_id}: {str(e)}")

        current_persona = persona_manager.get_current_persona()
        is_admin = user_id == config.ADMIN_USER_ID

        welcome_text = (
            "🤖 <b>Привет! Я ИИ-бот, созданный Javohir Zokirjonov</b>\n\n"
            f"🎭 <b>Текущий режим:</b> {current_persona.name}\n\n"
            "🚀 <b>Что умею:</b>\n"
            "💬 Разговоры с ИИ\n"
            "🖼️ Анализ изображений\n"
            "🎵 Распознавание речи\n"
            "🎮 Игры и развлечения\n\n"
            "🎯 <b>Просто пишите естественно!</b>\n"
            "🧮 <i>5+3*2</i>\n"
            "🌐 <i>Кнопки выбора языков в меню</i>\n"
            "🧠 <i>интересный факт</i>\n\n"
            "🌤️ <b>Погода по областям Узбекистана</b>\n"
            "<i>В меню инструментов → Погода</i>"
        )

        # Отправляем приветствие с клавиатурой
        await message.reply(
            welcome_text,
            reply_markup=keyboard_manager.get_main_menu(is_admin)
        )

    async def cmd_help(self, message: types.Message):
        """Обработчик команды /help."""
        user_id = message.from_user.id
        log_info("Получена команда /help", user_id)

        current_persona = persona_manager.get_current_persona()
        available_commands = persona_manager.get_available_commands()

        help_text = (
            "📚 <b>Справка по использованию</b>\n\n"
            f"🎭 <b>Текущий режим:</b> {current_persona.name}\n\n"
            "<b>Основные функции:</b>\n"
            "💬 Отправьте текст - получите умный ответ\n"
            "🖼️ Отправьте фото - анализ изображения\n"
            "🎵 Отправьте голосовое - распознавание речи\n\n"
            "<b>🎯 Естественный язык (ПРОСТО ПИШИТЕ!):</b>\n"
            "🧮 <i>2+2*5</i> - калькулятор\n"
            "🌐 <i>Кнопки выбора языков в меню</i> - перевод\n"
            "🧠 <i>интересный факт</i> - факты, шутки, цитаты\n\n"
            "<b>🌤️ Погода по областям Узбекистана:</b>\n"
            "• Кнопки в меню инструментов\n"
            "• 12 областей + Ташкент\n\n"
            "<b>Игры без команд:</b>\n"
            "🔢 Просто пиши числа в 'Угадай число'\n"
            "🧠 Пиши номера в 'Викторине'\n"
            "🪨 Пиши 'камень', 'ножницы', 'бумага'\n"
            "❓ Задавай вопросы 'Волшебному шару'\n\n"
            "<b>Режимы общения:</b>\n"
        )

        for cmd, desc in available_commands.items():
            help_text += f"{cmd} - {desc}\n"

        help_text += (
            "\n<b>Команды (если нужно):</b>\n"
            "/start - главное меню\n"
            "/help - эта справка\n"
            "/clear - очистить память\n\n"
            "🎯 <b>Главное:</b> Просто пишите естественно!\n"
            "Бот сам поймет что вы хотите:\n"
            "• Математика → калькулятор\n"
            "• Погода → прогноз\n"
            "• Перевод → переводчик\n"
            "• Факт/шутка → развлечения\n\n"
            "🚀 <b>Наслаждайтесь общением!</b>\n\n"
            "🤖 <i>Создан Javohir Zokirjonov</i>"
        )

        await message.reply(help_text)

    async def cmd_friendly(self, message: types.Message):
        """Переключение в дружелюбный режим."""
        user_id = message.from_user.id
        if persona_manager.set_persona(PersonaType.FRIENDLY):
            current = persona_manager.get_current_persona()
            log_info(f"Пользователь переключился в режим: {current.name}", user_id)

            # Сохраняем выбранную персону в память пользователя
            memory_manager.update_user_persona(user_id, current.name)

            await message.reply(f"🤗 Переключен в режим: <b>{current.name}</b>\n\n{current.description}")
        else:
            await message.reply("❌ Не удалось переключить режим")

    async def cmd_programmer(self, message: types.Message):
        """Переключение в режим программиста."""
        user_id = message.from_user.id
        if persona_manager.set_persona(PersonaType.PROGRAMMER):
            current = persona_manager.get_current_persona()
            log_info(f"Пользователь переключился в режим: {current.name}", user_id)

            # Сохраняем выбранную персону в память пользователя
            memory_manager.update_user_persona(user_id, current.name)

            await message.reply(f"💻 Переключен в режим: <b>{current.name}</b>\n\n{current.description}")
        else:
            await message.reply("❌ Не удалось переключить режим")

    async def cmd_expert(self, message: types.Message):
        """Переключение в экспертный режим."""
        user_id = message.from_user.id
        if persona_manager.set_persona(PersonaType.EXPERT):
            current = persona_manager.get_current_persona()
            log_info(f"Пользователь переключился в режим: {current.name}", user_id)
            await message.reply(f"🎓 Переключен в режим: <b>{current.name}</b>\n\n{current.description}")
        else:
            await message.reply("❌ Не удалось переключить режим")

    async def cmd_creative(self, message: types.Message):
        """Переключение в креативный режим."""
        user_id = message.from_user.id
        if persona_manager.set_persona(PersonaType.CREATIVE):
            current = persona_manager.get_current_persona()
            log_info(f"Пользователь переключился в режим: {current.name}", user_id)
            await message.reply(f"🎨 Переключен в режим: <b>{current.name}</b>\n\n{current.description}")
        else:
            await message.reply("❌ Не удалось переключить режим")

    async def cmd_professional(self, message: types.Message):
        """Переключение в профессиональный режим."""
        user_id = message.from_user.id
        if persona_manager.set_persona(PersonaType.PROFESSIONAL):
            current = persona_manager.get_current_persona()
            log_info(f"Пользователь переключился в режим: {current.name}", user_id)
            await message.reply(f"💼 Переключен в режим: <b>{current.name}</b>\n\n{current.description}")
        else:
            await message.reply("❌ Не удалось переключить режим")

    async def cmd_current_mode(self, message: types.Message):
        """Показать текущий режим."""
        user_id = message.from_user.id
        current = persona_manager.get_current_persona()
        log_info(f"Пользователь запросил текущий режим: {current.name}", user_id)

        mode_text = (
            f"🎭 <b>Текущий режим:</b> {current.name}\n\n"
            f"📝 {current.description}\n\n"
            "💡 <i>Все мои ответы теперь будут в стиле этого режима!</i>"
        )
        await message.reply(mode_text)

    async def cmd_calculate(self, message: types.Message):
        """Калькулятор для математических выражений."""
        user_id = message.from_user.id
        args = message.text.split(' ', 1)

        if len(args) < 2:
            await message.reply("🧮 <b>Калькулятор</b>\n\n"
                              "Использование: /calc <выражение>\n"
                              "Примеры:\n"
                              "• /calc 2 + 2\n"
                              "• /calc 5 * (3 + 2)\n"
                              "• /calc 10 / 3\n"
                              "• /calc 2^8")
            return

        expression = args[1].strip()
        result = calculator.evaluate_expression(expression)

        if result is not None:
            await message.reply(f"🧮 <b>Результат:</b>\n<code>{expression}</code> = <b>{result}</b>")
            log_info(f"Вычислено выражение: {expression} = {result}", user_id)
        else:
            await message.reply("❌ Не удалось вычислить выражение. Проверьте синтаксис.")
            log_error(f"Ошибка вычисления выражения: {expression}", user_id)


    async def cmd_game_rps(self, message: types.Message):
        """Игра камень-ножницы-бумага."""
        user_id = message.from_user.id
        args = message.text.split(' ', 1)

        if len(args) < 2:
            await message.reply("🪨 <b>Камень-Ножницы-Бумага</b>\n\n"
                              "Использование: /rps <выбор>\n"
                              "Варианты: камень, ножницы, бумага\n\n"
                              "Примеры:\n"
                              "• /rps камень\n"
                              "• /камень ножницы\n"
                              "• /rps бумага")
            return

        user_choice = args[1].strip().lower()
        result = game_service.play_rps(user_choice)

        await message.reply(result)
        log_info(f"Игра КНБ: пользователь выбрал {user_choice}", user_id)

    async def cmd_game_guess(self, message: types.Message):
        """Игра угадай число."""
        user_id = message.from_user.id
        args = message.text.split()

        if len(args) == 1:
            # Начинаем новую игру
            message_text, target_number = game_service.guess_number_game()
            # В реальном приложении нужно сохранить target_number для пользователя
            await message.reply(f"{message_text}\n\nИспользуй: /guess <число>")
            log_info("Начата игра угадай число", user_id)

        elif len(args) == 2:
            # Проверяем угаданное число
            try:
                guess = int(args[1])
                # В реальном приложении нужно получить сохраненное число для пользователя
                target_number = random.randint(1, 100)  # Заглушка
                result = game_service.check_guess(guess, target_number)
                await message.reply(result)
                log_info(f"Игра угадай число: {guess}", user_id)
            except ValueError:
                await message.reply("❌ Введите число!")

        else:
            await message.reply("🎮 <b>Угадай число</b>\n\n"
                              "• /guess - начать игру\n"
                              "• /guess <число> - угадать число")

    async def cmd_fun_fact(self, message: types.Message):
        """Интересный факт."""
        user_id = message.from_user.id
        fact = fun_service.get_random_fact()
        await message.reply(fact)
        log_info("Отправлен интересный факт", user_id)

    async def cmd_fun_quote(self, message: types.Message):
        """Мотивационная цитата."""
        user_id = message.from_user.id
        quote = fun_service.get_motivational_quote()
        await message.reply(quote)
        log_info("Отправлена мотивационная цитата", user_id)

    async def cmd_fun_joke(self, message: types.Message):
        """Шутка."""
        user_id = message.from_user.id
        joke = fun_service.get_random_joke()
        await message.reply(joke)
        log_info("Отправлена шутка", user_id)

    async def cmd_game_dice(self, message: types.Message):
        """Игра в кости."""
        user_id = message.from_user.id
        args = message.text.split()

        bet = 'medium'  # по умолчанию
        if len(args) > 1:
            bet = args[1].lower()

        if bet not in ['low', 'medium', 'high', 'низкий', 'средний', 'высокий']:
            await message.reply("🎲 <b>Игра в кости</b>\n\n"
                              "Использование: /dice <ставка>\n"
                              "Ставки: low/низкий, medium/средний, high/высокий\n\n"
                              "Примеры:\n"
                              "• /dice\n"
                              "• /кости средний\n"
                              "• /dice high")
            return

        # Преобразуем русские слова в английские
        if bet == 'низкий':
            bet = 'low'
        elif bet == 'средний':
            bet = 'medium'
        elif bet == 'высокий':
            bet = 'high'

        result = game_service.play_dice_game(bet)
        await message.reply(result)
        log_info(f"Игра в кости со ставкой {bet}", user_id)

    async def cmd_game_quiz(self, message: types.Message):
        """Викторина."""
        user_id = message.from_user.id

        question = game_service.get_random_question()
        await message.reply(question)
        log_info("Отправлен вопрос викторины", user_id)

    async def cmd_magic_ball(self, message: types.Message):
        """Волшебный шар."""
        user_id = message.from_user.id
        args = message.text.split(' ', 1)

        if len(args) < 2:
            await message.reply("🎱 <b>Волшебный шар</b>\n\n"
                              "Задай вопрос: /ball <вопрос>\n\n"
                              "Примеры:\n"
                              "• /шар Будет ли завтра дождь?\n"
                              "• /ball Я стану программистом?\n"
                              "• /волшебный Что ждет меня завтра?")
            return

        question = args[1]
        answer = game_service.get_magic_ball_answer()

        await message.reply(f"❓ <b>Твой вопрос:</b> {question}\n\n{answer}")
        log_info(f"Ответ волшебного шара на вопрос: {question[:50]}...", user_id)

    async def cmd_memory_clear(self, message: types.Message):
        """Очистить память разговора."""
        user_id = message.from_user.id

        # Импортируем здесь чтобы избежать циклических импортов
        from memory import memory_manager

        if memory_manager.clear_user_memory(user_id):
            await message.reply("🧠 <b>Память очищена!</b>\n\n"
                              "История нашего разговора удалена.\n"
                              "Теперь мы можем начать с чистого листа! ✨")
            log_info("Очищена память пользователя", user_id)
        else:
            await message.reply("❌ Не удалось очистить память")
            log_error("Ошибка очистки памяти", user_id)

    async def cmd_memory_stats(self, message: types.Message):
        """Показать статистику разговора."""
        user_id = message.from_user.id

        # Импортируем здесь чтобы избежать циклических импортов
        from memory import memory_manager

        stats = memory_manager.get_user_statistics(user_id)
        if stats:
            await message.reply(f"📊 <b>Статистика разговора</b>\n\n"
                              f"💬 Всего сообщений: {stats['total_messages']}\n"
                              f"🗂️ Текущих сообщений: {stats['current_messages']}\n"
                              f"📅 Создан: {stats['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
                              f"⏰ Длительность: {int(stats['conversation_duration'] / 3600)} ч {int((stats['conversation_duration'] % 3600) / 60)} мин")
            log_info("Показана статистика разговора", user_id)
        else:
            await message.reply("❌ Не удалось получить статистику")

    async def handle_callback(self, callback: types.CallbackQuery):
        """Обработчик нажатий на inline кнопки."""
        user_id = callback.from_user.id
        callback_data = callback.data

        log_info(f"Получен callback: {callback_data}", user_id)

        try:
            # Обработка меню
            if callback_data == "menu_personas":
                new_text = "🎭 <b>Выбери режим общения:</b>\n\nКаждый режим имеет свой уникальный стиль и специализацию!"
                current_text = callback.message.text or ""
                current_markup = callback.message.reply_markup

                # Проверяем, нужно ли обновлять сообщение
                if current_text != new_text or not self._is_same_markup(current_markup, keyboard_manager.get_personas_menu()):
                    await callback.message.edit_text(new_text, reply_markup=keyboard_manager.get_personas_menu())
                else:
                    await callback.answer("Меню уже открыто")

            elif callback_data == "menu_games":
                new_text = "🎮 <b>Игры и развлечения:</b>\n\nВыбери игру для веселого времяпрепровождения!"
                await self._safe_edit_message(callback, new_text, keyboard_manager.get_games_menu())

            elif callback_data == "menu_tools":
                new_text = "🛠️ <b>Инструменты и помощники:</b>\n\nПолезные инструменты для повседневных задач!"
                await self._safe_edit_message(callback, new_text, keyboard_manager.get_tools_menu())

            elif callback_data == "back_to_main":
                current_persona = persona_manager.get_current_persona()
                welcome_text = (
                    "🤖 <b>Привет! Я ИИ-бот, созданный Javohir Zokirjonov</b>\n\n"
                    f"🎭 <b>Текущий режим:</b> {current_persona.name}\n\n"
                    "🎮 <b>Выбери, чем займемся:</b>"
                )
                await self._safe_edit_message(callback, welcome_text, keyboard_manager.get_main_menu())

            # Обработка смены персоны
            elif callback_data.startswith("persona_"):
                persona_value = callback_data.split("_", 1)[1]
                persona_type = PersonaType(persona_value)

                if persona_manager.set_persona(persona_type):
                    current = persona_manager.get_current_persona()
                    memory_manager.update_user_persona(user_id, current.name)

                    success_text = (f"✅ <b>Режим изменен!</b>\n\n"
                                  f"🎭 <b>Текущий режим:</b> {current.name}\n\n"
                                  f"📝 {current.description}\n\n"
                                  f"💡 Все мои ответы теперь будут в стиле этого режима!")
                    await self._safe_edit_message(callback, success_text, keyboard_manager.get_personas_menu())
                else:
                    await callback.answer("❌ Не удалось изменить режим")

            # Обработка игр
            elif callback_data == "game_rps":
                rps_text = "🪨 <b>Камень-Ножницы-Бумага</b>\n\n🎯 <b>Выбери свой ход:</b>"
                await self._safe_edit_message(callback, rps_text, keyboard_manager.get_rps_choice_menu())

            elif callback_data.startswith("rps_"):
                user_choice = callback_data.split("_", 1)[1]
                result = game_service.play_rps(user_choice)

                result_text = f"🎮 <b>Результат игры:</b>\n\n{result}\n\n🎯 <b>Выбери свой следующий ход:</b>"
                await self._safe_edit_message(callback, result_text, keyboard_manager.get_rps_choice_menu())

                # Логируем статистику в БД
                try:
                    self.db.log_message(user_id, "game_rps", content=user_choice, response=result)
                    self.db.update_user_stats(user_id, "total_rps_games")
                except Exception as e:
                    log_error(f"Ошибка логирования игры КНБ пользователя {user_id}: {str(e)}")

            elif callback_data == "game_dice":
                new_text = "🎲 <b>Игра в кости</b>\n\nВыбери ставку:"
                await self._safe_edit_message(callback, new_text, keyboard_manager.get_dice_bet_menu())

            elif callback_data.startswith("dice_"):
                bet = callback_data.split("_", 1)[1]

                # Преобразование английских названий в русские для совместимости
                bet_map = {"low": "low", "medium": "medium", "high": "high"}
                bet = bet_map.get(bet, bet)

                result = game_service.play_dice_game(bet)
                result_text = f"🎯 <b>Результат игры в кости:</b>\n\n{result}"
                await self._safe_edit_message(callback, result_text, keyboard_manager.get_games_menu())

            elif callback_data == "game_guess":
                new_text = "🔢 <b>Угадай число</b>\n\nВыбери сложность:"
                await self._safe_edit_message(callback, new_text, keyboard_manager.get_guess_difficulty_menu())

            elif callback_data.startswith("guess_"):
                difficulty = callback_data.split("_", 1)[1]
                message_text, target_number = game_service.guess_number_game(difficulty)

                # Устанавливаем активную игру и сохраняем данные
                memory_manager.set_user_active_game(user_id, "guess_number", {
                    'target_number': target_number,
                    'difficulty': difficulty
                })

                result_text = f"🎮 {message_text}\n\n🎯 <b>Просто напиши число!</b> (без команд)"
                await self._safe_edit_message(callback, result_text, keyboard_manager.get_games_menu())

            elif callback_data == "game_quiz":
                # Генерируем вопрос викторины через Gemini AI
                quiz_data = game_service.generate_quiz_question()

                if quiz_data:
                    # Устанавливаем активную викторину с правильным ответом
                    memory_manager.set_user_active_game(user_id, "quiz", {
                        'correct_answer': quiz_data['correct_answer'],
                        'hint': quiz_data['hint'],
                        'options': quiz_data['options'],
                        'question': quiz_data['question']
                    })

                    quiz_text = f"🧠 <b>Викторина:</b>\n\n❓ {quiz_data['question']}\n\n🎯 <b>Выбери правильный ответ:</b>"
                    await self._safe_edit_message(callback, quiz_text, keyboard_manager.get_quiz_answers_menu(quiz_data['options']))
                else:
                    # Fallback на старый метод при ошибке AI
                    correct_answer = "1"
                    memory_manager.set_user_active_game(user_id, "quiz", {
                        'correct_answer': correct_answer
                    })

                    question = game_service.get_random_question()
                    quiz_text = f"🧠 <b>Викторина:</b>\n\n{question}\n\n🎯 <b>Просто напиши номер ответа!</b> (1-4)"
                    await self._safe_edit_message(callback, quiz_text, keyboard_manager.get_games_menu())

            elif callback_data == "game_ball":
                # Устанавливаем активную игру волшебный шар
                memory_manager.set_user_active_game(user_id, "magic_ball")

                ball_text = "🎱 <b>Волшебный шар</b>\n\n🎯 <b>Просто задай вопрос!</b>\nНапример: 'Будет ли завтра дождь?' или 'Стоит ли мне учиться?'"
                await self._safe_edit_message(callback, ball_text, keyboard_manager.get_games_menu())

            elif callback_data.startswith("quiz_answer_"):
                # Обработка ответа на викторину
                user_answer = callback_data.split("_", 2)[2]  # Получаем номер ответа (1, 2, 3, 4)
                game_data = memory_manager.get_user_game_data(user_id)

                if game_data and 'correct_answer' in game_data:
                    correct_answer = game_data['correct_answer']
                    question = game_data.get('question', '')
                    options = game_data.get('options', [])

                    result = game_service.check_quiz_answer(question, user_answer, correct_answer)

                    if "Правильно" in result:
                        # Викторина окончена
                        memory_manager.clear_user_active_game(user_id)
                        await callback.message.reply(f"🧠 {result}\n\nХочешь ответить на еще один вопрос? Нажми на кнопку '🧠 Викторина' в меню!", reply_markup=keyboard_manager.get_menu_button())

                        # Логируем статистику в БД
                        try:
                            self.db.update_user_stats(user_id, "total_quiz_games")
                        except Exception as e:
                            log_error(f"Ошибка логирования викторины пользователя {user_id}: {str(e)}")
                    else:
                        # Показываем подсказку и даем возможность выбрать другой ответ
                        hint = game_data.get('hint', 'Подсказка недоступна')
                        wrong_text = f"❌ <b>Неправильно!</b>\n\n💡 <b>Подсказка:</b> {hint}\n\n🎯 <b>Попробуй выбрать другой ответ:</b>"

                        if options:
                            await self._safe_edit_message(callback, wrong_text, keyboard_manager.get_quiz_answers_menu(options))
                        else:
                            await callback.answer("❌ Ошибка загрузки вариантов ответов")
                else:
                    await callback.answer("❌ Игра не найдена")

            elif callback_data == "quiz_hint":
                # Показываем подсказку для викторины
                game_data = memory_manager.get_user_game_data(user_id)

                if game_data and 'hint' in game_data and 'question' in game_data:
                    question = game_data['question']
                    hint = game_data['hint']
                    options = game_data.get('options', [])

                    # Создаем новый текст с подсказкой
                    hint_text = f"🧠 <b>Викторина:</b>\n\n❓ {question}\n\n💡 <b>Подсказка:</b> {hint}\n\n🎯 <b>Выбери правильный ответ:</b>"

                    # Проверяем, отличается ли новый текст от текущего
                    current_text = callback.message.text or ""
                    if current_text != hint_text and options:
                        await self._safe_edit_message(callback, hint_text, keyboard_manager.get_quiz_answers_menu(options))
                    else:
                        await callback.answer("💡 Подсказка уже показана!")
                else:
                    await callback.answer("❌ Подсказка недоступна")

            # Обработка инструментов
            elif callback_data == "tool_calc":
                calc_text = ("🧮 <b>Калькулятор</b>\n\n"
                           "Используй команду: /calc &lt;выражение&gt;\n\n"
                           "Примеры:\n"
                           "• /calc 2 + 2\n"
                           "• /calc 5 * (3 + 2)\n"
                           "• /calc 2^8")
                await self._safe_edit_message(callback, calc_text, keyboard_manager.get_tools_menu())

            elif callback_data == "tool_weather":
                weather_text = "🌤️ <b>Выберите область Узбекистана</b>\n\nВыберите область для получения прогноза погоды:"
                await self._safe_edit_message(callback, weather_text, keyboard_manager.get_uzbekistan_weather_menu())

            elif callback_data == "tool_translate":
                translate_text = "🌐 <b>Выберите язык для перевода</b>\n\nВыберите целевой язык и затем введите текст для перевода:"
                await self._safe_edit_message(callback, translate_text, keyboard_manager.get_translation_languages_menu())

            # Развлечения
            elif callback_data == "fun_joke":
                joke = fun_service.get_random_joke()
                joke_text = f"🤣 <b>Шутка:</b>\n\n{joke}"
                await self._safe_edit_message(callback, joke_text, keyboard_manager.get_tools_menu())

            elif callback_data == "fun_quote":
                quote = fun_service.get_motivational_quote()
                quote_text = f"💡 <b>Мотивационная цитата:</b>\n\n{quote}"
                await self._safe_edit_message(callback, quote_text, keyboard_manager.get_tools_menu())

            elif callback_data == "fun_fact":
                fact = fun_service.get_random_fact()
                await self._safe_edit_message(callback, fact, keyboard_manager.get_tools_menu())

            # Служебные функции
            elif callback_data == "stats":
                stats = memory_manager.get_user_statistics(user_id)
                if stats:
                    stats_text = (f"📊 <b>Статистика твоего общения со мной:</b>\n\n"
                                f"💬 Всего сообщений: {stats['total_messages']}\n"
                                f"🗂️ Сохранено в памяти: {stats['current_messages']}\n"
                                f"📅 Начали общаться: {stats['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
                                f"⏰ Времени прошло: {int(stats['conversation_duration'] / 3600)} ч {int((stats['conversation_duration'] % 3600) / 60)} мин")
                    await self._safe_edit_message(callback, stats_text, keyboard_manager.get_main_menu())
                else:
                    await self._safe_edit_message(callback, "❌ Не удалось получить статистику", keyboard_manager.get_main_menu())

            elif callback_data == "clear_memory":
                confirm_text = (
                    "🧠 <b>Очистка памяти</b>\n\n"
                    "⚠️ Это действие удалит всю историю нашего разговора!\n\n"
                    "Ты уверен, что хочешь очистить память?"
                )
                await self._safe_edit_message(callback, confirm_text, keyboard_manager.get_confirmation_menu("clear_memory", "confirm_clear_memory"))

            elif callback_data == "confirm_clear_memory":
                if memory_manager.clear_user_memory(user_id):
                    success_text = ("🧠 <b>Память очищена!</b>\n\n"
                                  "✅ История нашего разговора удалена\n"
                                  "🔄 Теперь мы можем начать с чистого листа!\n\n"
                                  "Используй /start для главного меню")
                    await self._safe_edit_message(callback, success_text, keyboard_manager.get_main_menu())
                else:
                    await self._safe_edit_message(callback, "❌ Не удалось очистить память", keyboard_manager.get_main_menu())

            elif callback_data == "help":
                current_persona = persona_manager.get_current_persona()
                available_commands = persona_manager.get_available_commands()

                help_text = (
                    "📚 <b>Справка по использованию</b>\n\n"
                    f"🎭 <b>Текущий режим:</b> {current_persona.name}\n\n"
                    "<b>🎮 Кнопки:</b>\n"
                    "• Режимы общения - выбор стиля разговора\n"
                    "• Игры - просто нажимай и играй!\n"
                    "• Инструменты - калькулятор, погода, перевод\n\n"
                    "<b>🎯 Удобство:</b>\n"
                    "• В играх просто пиши ответы (числа, слова)\n"
                    "• Для общения просто пиши сообщения\n"
                    "• Все интуитивно и без лишних команд!\n\n"
                    "<b>🎮 Игры без команд:</b>\n"
                    "• Угадай число - просто пиши числа\n"
                    "• Викторина - пиши номер ответа (1-4)\n"
                    "• КНБ - пиши: камень, ножницы, бумага\n"
                    "• Волшебный шар - просто задай вопрос\n\n"
                    "🤖 <i>Создан Javohir Zokirjonov</i>"
                )

                await self._safe_edit_message(callback, help_text, keyboard_manager.get_main_menu())

            elif callback_data == "cancel":
                await self._safe_edit_message(callback, "❌ Действие отменено", keyboard_manager.get_main_menu())

            # Обработка областей Узбекистана для погоды
            elif callback_data.startswith("weather_"):
                await self._handle_weather_region_callback(callback, callback_data)

            # Обработка выбора языков для перевода
            elif callback_data.startswith("lang_"):
                await self._handle_translation_language_callback(callback, callback_data)

            # Быстрый доступ к меню
            elif callback_data == "show_main_menu":
                current_persona = persona_manager.get_current_persona()
                is_admin = callback.from_user.id == config.ADMIN_USER_ID
                menu_text = (
                    "🤖 <b>Главное меню</b>\n\n"
                    f"🎭 <b>Текущий режим:</b> {current_persona.name}\n\n"
                    "🎮 <b>Выбери, чем займемся:</b>"
                )
                await self._safe_edit_message(callback, menu_text, keyboard_manager.get_main_menu(is_admin))

            # Админ-панель
            elif callback_data == "admin_panel":
                if callback.from_user.id == config.ADMIN_USER_ID:
                    admin_text = "👑 <b>Админ-панель</b>\n\nВыберите действие для управления ботом:"
                    await self._safe_edit_message(callback, admin_text, keyboard_manager.get_admin_menu())
                else:
                    await callback.answer("❌ У вас нет доступа к админ-панели")

            elif callback_data == "admin_main":
                if callback.from_user.id == config.ADMIN_USER_ID:
                    admin_text = "👑 <b>Админ-панель</b>\n\nВыберите действие для управления ботом:"
                    await self._safe_edit_message(callback, admin_text, keyboard_manager.get_admin_menu())
                else:
                    await callback.answer("❌ У вас нет доступа к админ-панели")

            elif callback_data.startswith("admin_"):
                if callback.from_user.id == config.ADMIN_USER_ID:
                    await self._handle_admin_callback(callback, callback_data)
                else:
                    await callback.answer("❌ У вас нет доступа к админ-панели")

            # Неизвестная callback
            else:
                await callback.answer("❓ Неизвестная команда")

            # Отвечаем на callback query
            await callback.answer()

        except Exception as e:
            log_error(f"Ошибка при обработке callback {callback_data}: {str(e)}", user_id, e)
            await callback.answer("❌ Произошла ошибка")

    async def _handle_weather_region_callback(self, callback: types.CallbackQuery, callback_data: str):
        """Обработка выбора области Узбекистана для погоды."""
        user_id = callback.from_user.id

        # Словарь соответствия callback_data и названий городов/областей
        region_map = {
            "weather_tashkent": "Ташкент",
            "weather_andijan": "Андижан",
            "weather_bukhara": "Бухара",
            "weather_jizzakh": "Джизак",
            "weather_karakalpakstan": "Нукус",  # Столица Каракалпакстана
            "weather_kashkadarya": "Карши",
            "weather_namangan": "Наманган",
            "weather_navoi": "Навои",
            "weather_samarkand": "Самарканд",
            "weather_surkhondarya": "Термез",
            "weather_syrdarya": "Гулистан",
            "weather_tashkent_region": "Чирчик",  # Крупный город Ташкентской области
            "weather_fergana": "Фергана",
            "weather_khorezm": "Ургенч"
        }

        region_name = region_map.get(callback_data, callback_data.replace("weather_", "").title())

        # Получаем погоду
        weather_info = weather_service.get_weather(region_name)

        if weather_info:
            # Показываем погоду и возвращаемся к меню областей
            weather_text = f"🌤️ <b>Погода в {region_name}</b>\n\n{weather_info}\n\nВыберите другую область:"
            await self._safe_edit_message(callback, weather_text, keyboard_manager.get_uzbekistan_weather_menu())
            log_info(f"Показана погода для {region_name}", user_id)
        else:
            # Ошибка получения погоды
            error_text = f"❌ Не удалось получить погоду для {region_name}.\n\nПопробуйте выбрать другую область:"
            await self._safe_edit_message(callback, error_text, keyboard_manager.get_uzbekistan_weather_menu())
            log_error(f"Ошибка получения погоды для {region_name}", user_id)

    async def _handle_translation_language_callback(self, callback: types.CallbackQuery, callback_data: str):
        """Обработка выбора языка для перевода."""
        user_id = callback.from_user.id

        # Словарь соответствия callback_data и кодов языков
        lang_map = {
            "lang_uz": "uz",
            "lang_ru": "ru",
            "lang_en": "en",
            "lang_es": "es",
            "lang_fr": "fr",
            "lang_de": "de",
            "lang_it": "it",
            "lang_pt": "pt",
            "lang_zh": "zh",
            "lang_ja": "ja",
            "lang_ko": "ko"
        }

        # Словарь соответствия кодов языков и названий
        lang_names = {
            "uz": "🇺🇿 узбекский",
            "ru": "🇷🇺 русский",
            "en": "🇺🇸 английский",
            "es": "🇪🇸 испанский",
            "fr": "🇫🇷 французский",
            "de": "🇩🇪 немецкий",
            "it": "🇮🇹 итальянский",
            "pt": "🇵🇹 португальский",
            "zh": "🇨🇳 китайский",
            "ja": "🇯🇵 японский",
            "ko": "🇰🇷 корейский"
        }

        target_lang = lang_map.get(callback_data)
        lang_name = lang_names.get(target_lang, callback_data.replace("lang_", "").title())

        if target_lang:
            # Сохраняем выбранный язык в памяти пользователя
            memory_manager.set_user_active_game(user_id, f"translate_{target_lang}", {})

            # Показываем сообщение о выборе языка
            translate_text = f"🌐 <b>Выбран язык:</b> {lang_name}\n\n<i>Теперь просто введите текст для перевода!</i>\n\nПример: Привет мир"
            await self._safe_edit_message(callback, translate_text, keyboard_manager.get_translation_languages_menu())

            log_info(f"Пользователь {user_id} выбрал язык для перевода: {target_lang}", user_id)
        else:
            await callback.answer("❌ Ошибка выбора языка")

    async def _handle_admin_callback(self, callback: types.CallbackQuery, callback_data: str):
        """Обработка админских callback'ов."""
        user_id = callback.from_user.id

        try:
            if callback_data == "admin_users":
                users_text = "👥 <b>Управление пользователями</b>\n\nВыберите действие:"
                await self._safe_edit_message(callback, users_text, keyboard_manager.get_admin_users_menu())

            elif callback_data == "admin_stats":
                stats_text = "📊 <b>Просмотр статистики</b>\n\nВыберите тип статистики:"
                await self._safe_edit_message(callback, stats_text, keyboard_manager.get_admin_stats_menu())

            elif callback_data == "admin_search":
                search_text = "🔍 <b>Поиск пользователей</b>\n\nВыберите способ поиска:"
                await self._safe_edit_message(callback, search_text, keyboard_manager.get_admin_search_menu())

            elif callback_data == "admin_users_list":
                await self._show_users_list(callback)

            elif callback_data == "admin_top_users":
                await self._show_top_users(callback)

            elif callback_data == "admin_stats_general":
                await self._show_general_stats(callback)

            elif callback_data == "admin_stats_games":
                await self._show_games_stats(callback)

            elif callback_data == "admin_stats_messages":
                await self._show_messages_stats(callback)

            elif callback_data.startswith("admin_clear_user"):
                await self._handle_clear_user(callback)

            elif callback_data == "admin_clear_all":
                await self._handle_clear_all_users(callback)

            elif callback_data == "confirm_clear_all":
                await self._confirm_clear_all_users(callback)

            elif callback_data.startswith("admin_ban_user"):
                await self._handle_ban_user(callback)

            elif callback_data.startswith("admin_unban_user"):
                await self._handle_unban_user(callback)

            else:
                await callback.answer("❓ Неизвестная админская команда")

        except Exception as e:
            log_error(f"Ошибка при обработке админской команды {callback_data}: {str(e)}")
            await callback.answer("❌ Произошла ошибка при обработке команды")

    async def _show_users_list(self, callback: types.CallbackQuery):
        """Показать список пользователей."""
        try:
            users = self.db.get_all_users(limit=20)

            if not users:
                text = "👥 <b>Список пользователей</b>\n\nПользователи не найдены."
            else:
                text = "👥 <b>Список пользователей</b>\n\n"
                for user in users:
                    status = "🚫" if user.get('banned_until') else "✅"
                    username = f"@{user['username']}" if user['username'] else "без username"
                    text += f"{status} <code>{user['id']}</code> - {user['first_name']} ({username})\n"
                    text += f"   📊 Сообщений: {user['total_messages']} | 🎮 Игр: {user['total_games']}\n\n"

                text += f"Всего пользователей: {len(users)}"

            await self._safe_edit_message(callback, text, keyboard_manager.get_admin_users_menu())

        except Exception as e:
            log_error(f"Ошибка получения списка пользователей: {str(e)}")
            await callback.answer("❌ Ошибка загрузки списка пользователей")

    async def _show_top_users(self, callback: types.CallbackQuery):
        """Показать топ пользователей по различным метрикам."""
        try:
            # Получить топ пользователей по сообщениям
            users = self.db.get_all_users(limit=10)

            if not users:
                text = "👑 <b>Топ пользователей</b>\n\nПользователи не найдены."
            else:
                text = "👑 <b>Топ 10 активных пользователей</b>\n\n"

                for i, user in enumerate(users[:10], 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "⭐"
                    username = f"@{user['username']}" if user['username'] else "без username"
                    text += f"{medal} <b>{i}.</b> <code>{user['id']}</code>\n"
                    text += f"   👤 {user['first_name']} ({username})\n"
                    text += f"   📊 Сообщений: {user['total_messages']}\n"
                    text += f"   🎮 Игр: {user['total_games']} | 🌐 Переводов: {user['total_translations']}\n\n"

            await self._safe_edit_message(callback, text, keyboard_manager.get_admin_search_menu())

        except Exception as e:
            log_error(f"Ошибка получения топ пользователей: {str(e)}")
            await callback.answer("❌ Ошибка загрузки топ пользователей")

    async def _show_general_stats(self, callback: types.CallbackQuery):
        """Показать общую статистику."""
        try:
            stats = self.db.get_system_stats()

            text = "📊 <b>Общая статистика бота</b>\n\n"
            text += f"👥 Пользователей: {stats['total_users']}\n"
            text += f"💬 Сообщений: {stats['total_messages']}\n"
            text += f"🎮 Игровых сессий: {stats['total_games']}\n\n"

            text += "<b>Типы сообщений:</b>\n"
            for msg_type, count in stats['message_types'].items():
                text += f"• {msg_type}: {count}\n"

            await self._safe_edit_message(callback, text, keyboard_manager.get_admin_stats_menu())

        except Exception as e:
            log_error(f"Ошибка получения общей статистики: {str(e)}")
            await callback.answer("❌ Ошибка загрузки статистики")

    async def _show_games_stats(self, callback: types.CallbackQuery):
        """Показать статистику игр."""
        try:
            text = "🎮 <b>Статистика игр</b>\n\n"
            text += "Функция находится в разработке...\n"
            text += "Пока что доступна только общая статистика в разделе '📊 Общая статистика'"

            await self._safe_edit_message(callback, text, keyboard_manager.get_admin_stats_menu())

        except Exception as e:
            log_error(f"Ошибка получения статистики игр: {str(e)}")
            await callback.answer("❌ Ошибка загрузки статистики игр")

    async def _show_messages_stats(self, callback: types.CallbackQuery):
        """Показать статистику сообщений."""
        try:
            text = "💬 <b>Статистика сообщений</b>\n\n"
            text += "Функция находится в разработке...\n"
            text += "Пока что доступна только общая статистика в разделе '📊 Общая статистика'"

            await self._safe_edit_message(callback, text, keyboard_manager.get_admin_stats_menu())

        except Exception as e:
            log_error(f"Ошибка получения статистики сообщений: {str(e)}")
            await callback.answer("❌ Ошибка загрузки статистики сообщений")

    async def _handle_clear_user(self, callback: types.CallbackQuery):
        """Обработка очистки статистики пользователя."""
        text = "🧹 <b>Очистка статистики пользователя</b>\n\n"
        text += "Введите ID пользователя, статистику которого нужно очистить:\n\n"
        text += "<i>Пример: 123456789</i>\n\n"
        text += "После ввода ID будет предложено подтверждение."

        await self._safe_edit_message(callback, text, keyboard_manager.get_admin_users_menu())

    async def _handle_clear_all_users(self, callback: types.CallbackQuery):
        """Обработка очистки статистики всех пользователей."""
        text = "🗑️ <b>Очистка ВСЕЙ статистики</b>\n\n"
        text += "⚠️ <b>ВНИМАНИЕ!</b> Это действие нельзя отменить!\n\n"
        text += "Будут удалены:\n"
        text += "• Вся статистика пользователей\n"
        text += "• История сообщений\n"
        text += "• Данные игровых сессий\n"
        text += "• Настройки пользователей\n\n"
        text += "Вы действительно хотите продолжить?"

        confirm_markup = keyboard_manager.get_confirmation_menu("Очистить всю статистику", "confirm_clear_all")
        await self._safe_edit_message(callback, text, confirm_markup)

    async def _handle_ban_user(self, callback: types.CallbackQuery):
        """Обработка бана пользователя."""
        text = "🚫 <b>Блокировка пользователя</b>\n\n"
        text += "Введите ID пользователя для блокировки:\n\n"
        text += "<i>Пример: 123456789</i>\n\n"
        text += "Пользователь сможет использовать бота только через 24 часа."

        await self._safe_edit_message(callback, text, keyboard_manager.get_admin_users_menu())

    async def _handle_unban_user(self, callback: types.CallbackQuery):
        """Обработка разбана пользователя."""
        text = "✅ <b>Разблокировка пользователя</b>\n\n"
        text += "Введите ID пользователя для разблокировки:\n\n"
        text += "<i>Пример: 123456789</i>"

        await self._safe_edit_message(callback, text, keyboard_manager.get_admin_users_menu())

    async def _confirm_clear_all_users(self, callback: types.CallbackQuery):
        """Подтверждение очистки всех данных пользователей."""
        try:
            # Выполняем очистку
            self.db.clear_all_users_stats()

            text = "✅ <b>Очистка завершена!</b>\n\n"
            text += "🗑️ Статистика всех пользователей была успешно очищена:\n"
            text += "• Сообщения\n"
            text += "• Игровые сессии\n"
            text += "• История переводов\n"
            text += "• Данные калькулятора\n"
            text += "• Факты и шутки\n\n"
            text += "📊 <b>Примечание:</b> Пользователи остаются в системе"

            await self._safe_edit_message(callback, text, keyboard_manager.get_admin_users_menu())

        except Exception as e:
            log_error(f"Ошибка при очистке всех данных: {str(e)}")
            error_text = "❌ <b>Ошибка при очистке данных</b>\n\n"
            error_text += f"Произошла ошибка: {str(e)}\n\n"
            error_text += "Попробуйте еще раз или обратитесь к разработчику"

            await self._safe_edit_message(callback, error_text, keyboard_manager.get_admin_users_menu())

    def _is_same_markup(self, markup1, markup2) -> bool:
        """Проверяет, одинаковые ли клавиатуры."""
        if not markup1 or not markup2:
            return False
        try:
            return (markup1.inline_keyboard == markup2.inline_keyboard)
        except:
            return False

    async def _safe_edit_message(self, callback, text: str, reply_markup=None):
        """Безопасное редактирование сообщения с проверкой изменений."""
        try:
            current_text = callback.message.text or ""
            current_markup = callback.message.reply_markup

            # Проверяем, нужно ли обновлять
            if current_text != text or not self._is_same_markup(current_markup, reply_markup):
                await callback.message.edit_text(text, reply_markup=reply_markup)
            else:
                await callback.answer("Уже открыто")
        except Exception as e:
            log_error(f"Ошибка при редактировании сообщения: {str(e)}")
            await callback.answer("Ошибка обновления")

    async def show_main_menu(self, message: types.Message):
        """Показать главное меню с кнопками."""
        user_id = message.from_user.id
        log_info("Показ главного меню", user_id)

        current_persona = persona_manager.get_current_persona()

        welcome_text = (
            "🤖 <b>Главное меню</b>\n\n"
            f"🎭 <b>Текущий режим:</b> {current_persona.name}\n\n"
            "🎮 <b>Выбери, чем займемся:</b>"
        )

        await message.reply(
            welcome_text,
            reply_markup=keyboard_manager.get_main_menu()
        )

    async def handle_text_message(self, message: types.Message):
        """Обработчик текстовых сообщений."""
        user_id = message.from_user.id
        text = message.text.strip()

        log_info(f"Получено текстовое сообщение: {text[:100]}...", user_id)

        # Проверяем, не является ли сообщение запросом к инструменту
        tool_response = await self._check_tool_request(user_id, text, message)
        if tool_response:
            return

        # Проверяем, не является ли сообщение ответом на активную игру
        game_response = await self._check_game_response(user_id, text, message)
        if game_response:
            return

        # Сохраняем сообщение пользователя в память
        memory_manager.add_user_message(user_id, text, 'text')

        # Отправляем индикатор "печатает"
        await message.bot.send_chat_action(message.chat.id, "typing")

        try:
            # Получаем контекст разговора для более умных ответов
            context = memory_manager.get_user_context(user_id)

            # Генерируем ответ через Gemini с учетом контекста
            if context:
                # Добавляем контекст к сообщению
                enhanced_text = f"Контекст предыдущего разговора:\n{context}\n\nТекущее сообщение пользователя: {text}"
            else:
                enhanced_text = text

            response = gemini_client.generate_text_response(enhanced_text)

            if response:
                # Ограничиваем длину ответа (Telegram имеет лимит)
                if len(response) > 4000:
                    response = response[:4000] + "...\n\n<i>Ответ был обрезан из-за ограничений Telegram</i>"

                await message.reply(response, reply_markup=keyboard_manager.get_menu_button())
                log_info("Отправлен ответ на текстовое сообщение", user_id)

                # Логируем статистику в БД
                try:
                    self.db.log_message(user_id, "text", content=text, response=response)
                    self.db.update_user_stats(user_id, "total_messages")
                except Exception as e:
                    log_error(f"Ошибка логирования сообщения пользователя {user_id}: {str(e)}")

                # Сохраняем ответ ассистента в память
                memory_manager.add_assistant_message(user_id, response, 'text')
            else:
                error_msg = "❌ Извините, не удалось обработать ваш запрос. Попробуйте позже."
                await message.reply(error_msg)
                log_error("Не удалось сгенерировать ответ на текстовое сообщение", user_id)

                # Сохраняем сообщение об ошибке в память
                memory_manager.add_assistant_message(user_id, error_msg, 'text')

        except Exception as e:
            log_error(f"Ошибка при обработке текстового сообщения: {str(e)}", user_id, e)
            error_msg = "❌ Произошла ошибка при обработке вашего сообщения."
            await message.reply(error_msg)

            # Сохраняем сообщение об ошибке в память
            memory_manager.add_assistant_message(user_id, error_msg, 'text')

    async def _check_game_response(self, user_id: int, text: str, message: types.Message) -> bool:
        """Проверяет, является ли сообщение ответом на активную игру."""
        active_game = memory_manager.get_user_active_game(user_id)

        if not active_game:
            return False

        try:
            if active_game == "guess_number":
                # Проверяем, является ли текст числом
                if text.isdigit():
                    guess = int(text)
                    game_data = memory_manager.get_user_game_data(user_id)
                    target_number = game_data.get('target_number')

                    if target_number:
                        result = game_service.check_guess(guess, target_number)

                        if "Правильно" in result:
                            # Игра окончена
                            memory_manager.clear_user_active_game(user_id)
                            await message.reply(f"🎉 {result}\n\nХочешь сыграть еще раз? Нажми на кнопку '🔢 Угадай число' в меню!", reply_markup=keyboard_manager.get_menu_button())

                            # Логируем статистику в БД
                            try:
                                self.db.update_user_stats(user_id, "total_games")
                            except Exception as e:
                                log_error(f"Ошибка логирования угадай числа пользователя {user_id}: {str(e)}")

                            return True  # Завершаем обработку игры
                        else:
                            await message.reply(f"🎯 {result}", reply_markup=keyboard_manager.get_menu_button())
                            return True  # Важно вернуть True, чтобы игра продолжилась

            elif active_game == "quiz":
                # Проверяем, является ли текст числом от 1 до 4
                if text.isdigit() and 1 <= int(text) <= 4:
                    game_data = memory_manager.get_user_game_data(user_id)
                    correct_answer = game_data.get('correct_answer')
                    question = game_data.get('question', '')

                    if correct_answer:
                        result = game_service.check_quiz_answer(question, text, correct_answer)

                        if "Правильно" in result:
                            # Викторина окончена
                            memory_manager.clear_user_active_game(user_id)
                            await callback.message.reply(f"🧠 {result}\n\nХочешь ответить на еще один вопрос? Нажми на кнопку '🧠 Викторина' в меню!", reply_markup=keyboard_manager.get_menu_button())

                            # Логируем статистику в БД
                            try:
                                self.db.update_user_stats(user_id, "total_quiz_games")
                            except Exception as e:
                                log_error(f"Ошибка логирования викторины пользователя {user_id}: {str(e)}")

                            return True  # Завершаем обработку викторины
                        else:
                            # Для викторины с кнопками - показываем подсказку и даем выбрать другой ответ
                            game_data = memory_manager.get_user_game_data(user_id)
                            hint = game_data.get('hint', 'Подсказка недоступна') if game_data else 'Подсказка недоступна'
                            options = game_data.get('options', []) if game_data else []

                            if options:
                                # Если есть данные викторины, показываем кнопки для повторного выбора
                                wrong_text = f"❌ <b>Неправильно!</b>\n\n💡 <b>Подсказка:</b> {hint}\n\n🎯 <b>Попробуй выбрать другой ответ:</b>"
                                await message.reply(wrong_text, reply_markup=keyboard_manager.get_quiz_answers_menu(options))
                            else:
                                # Fallback для старого формата
                                await message.reply(f"📚 {result}", reply_markup=keyboard_manager.get_menu_button())
                        return True

            elif active_game == "rps":
                # Проверяем выбор в камень-ножницы-бумага
                choices = ['камень', 'ножницы', 'бумага']
                if text.lower() in choices:
                    result = game_service.play_rps(text.lower())
                    memory_manager.clear_user_active_game(user_id)
                    await message.reply(f"🎮 <b>Результат игры:</b>\n\n{result}\n\nХочешь сыграть еще? Нажми '🪨 Камень-Ножницы-Бумага'!", reply_markup=keyboard_manager.get_menu_button())
                    return True

            elif active_game == "magic_ball":
                # Любой текст считается вопросом к волшебному шару
                if len(text.strip()) > 0:
                    answer = game_service.get_magic_ball_answer(text.strip())
                    memory_manager.clear_user_active_game(user_id)
                    await message.reply(f"❓ <b>Твой вопрос:</b> {text}\n\n{answer}\n\nХочешь спросить еще? Нажми '🎱 Волшебный шар'!", reply_markup=keyboard_manager.get_menu_button())

                    # Логируем статистику в БД
                    try:
                        self.db.log_message(user_id, "magic_ball", content=text.strip(), response=answer)
                        # Волшебный шар можно считать как мини-игру, но не добавляем в total_games
                    except Exception as e:
                        log_error(f"Ошибка логирования волшебного шара пользователя {user_id}: {str(e)}")
                    return True

            elif active_game.startswith("translate_"):
                # Обработка текста для перевода
                if len(text.strip()) > 0:
                    target_lang = active_game.replace("translate_", "")
                    translation = translator.translate_text(text, target_lang)

                    if translation:
                        memory_manager.clear_user_active_game(user_id)
                        await message.reply(f"🌐 <b>Перевод на {translator.SUPPORTED_LANGUAGES.get(target_lang, target_lang)}:</b>\n\n{translation}\n\nХочешь перевести еще текст? Выбери язык в меню '🌐 Переводчик'!", reply_markup=keyboard_manager.get_menu_button())
                        log_info(f"Выполнен перевод на {target_lang}: {text[:50]}...", user_id)
                    else:
                        await message.reply("❌ Не удалось выполнить перевод. Попробуйте другой текст.")
                        log_error(f"Ошибка перевода текста на {target_lang}: {text}", user_id)
                    return True

        except Exception as e:
            log_error(f"Ошибка при обработке ответа на игру {active_game}: {str(e)}", user_id)
            await message.reply("❌ Произошла ошибка. Попробуй начать заново!")

        return False

    async def _check_tool_request(self, user_id: int, text: str, message: types.Message) -> bool:
        """Проверяет, является ли сообщение запросом к инструменту (без команды)."""
        text_lower = text.lower().strip()

        try:
            # Проверка на запрос погоды
            weather_keywords = ['погода', 'погодка', 'какая погода', 'weather', 'температура', 'прогноз']
            if any(keyword in text_lower for keyword in weather_keywords):
                # Извлекаем город из текста
                city = self._extract_city_from_weather_request(text)
                if city:
                    return await self._process_weather_request(user_id, city, message)
                else:
                    await message.reply("🌤️ <b>Погода</b>\n\n"
                                      "Просто напиши: <i>погода в [город]</i>\n"
                                      "Например: погода в Москве, какая погода в Ташкенте")
                    return True

            # Проверка на запрос перевода
            translate_keywords = ['переведи', 'перевод', 'translate', 'translation']
            if any(keyword in text_lower for keyword in translate_keywords):
                # Извлекаем язык и текст для перевода
                lang, text_to_translate = self._extract_translation_from_request(text)
                if lang and text_to_translate:
                    return await self._process_translation_request(user_id, lang, text_to_translate, message)
                else:
                    await message.reply("🌐 <b>Переводчик</b>\n\n"
                                      "Просто напиши: <i>переведи на [язык] [текст]</i>\n"
                                      "Языки: ru, en, es, fr, de, it, pt, zh, ja, ko\n\n"
                                      "Примеры:\n"
                                      "• переведи на английский привет мир\n"
                                      "• translate to russian hello world")
                    return True

            # Проверка на математический запрос
            if self._is_math_expression(text):
                return await self._process_calc_request(user_id, text, message)

            # Проверка на запрос фактов/шуток/цитат
            fun_keywords = ['факт', 'шутка', 'цитата', 'fact', 'joke', 'quote', 'интересное', 'интересный факт']
            if any(keyword in text_lower for keyword in fun_keywords):
                return await self._process_fun_request(user_id, text, message)

            return False

        except Exception as e:
            log_error(f"Ошибка при обработке запроса инструмента: {str(e)}", user_id)
            await message.reply("❌ Произошла ошибка при обработке запроса.")
            return True

    def _extract_city_from_weather_request(self, text: str) -> Optional[str]:
        """Извлекает название города из запроса погоды."""
        # Удаляем ключевые слова и оставляем только город
        text = text.lower()
        for keyword in ['погода', 'погодка', 'какая погода', 'weather', 'температура', 'прогноз', 'в', 'на', 'во']:
            text = text.replace(keyword, '')

        # Удаляем лишние пробелы и знаки препинания
        city = text.strip(' ,.!?').title()

        if len(city) > 1:
            return city
        return None

    async def _process_weather_request(self, user_id: int, city: str, message: types.Message) -> bool:
        """Обрабатывает запрос погоды."""
        weather_info = weather_service.get_weather(city)

        if weather_info:
            await message.reply(weather_info, reply_markup=keyboard_manager.get_menu_button())
            log_info(f"Отправлена погода для города: {city}", user_id)

            # Логируем статистику в БД
            try:
                self.db.log_message(user_id, "weather", content=city, response=weather_info)
                self.db.update_user_stats(user_id, "total_weather_requests")
            except Exception as e:
                log_error(f"Ошибка логирования погоды пользователя {user_id}: {str(e)}")
        else:
            await message.reply(f"❌ Не удалось получить погоду для города '{city}'. Попробуйте другой город.")
            log_error(f"Не удалось получить погоду для города: {city}", user_id)

        return True

    def _extract_translation_from_request(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Извлекает язык и текст для перевода."""
        text_lower = text.lower()

        # Ищем паттерн "переведи на [язык] [текст]"
        import re

        # Русский паттерн
        ru_match = re.search(r'переведи\s+на\s+(\w+)\s+(.+)', text_lower, re.IGNORECASE)
        if ru_match:
            lang = ru_match.group(1).lower()
            text_to_translate = ru_match.group(2).strip()
            return lang, text_to_translate

        # Английский паттерн
        en_match = re.search(r'translate\s+to\s+(\w+)\s+(.+)', text_lower, re.IGNORECASE)
        if en_match:
            lang = en_match.group(1).lower()
            text_to_translate = en_match.group(2).strip()
            return lang, text_to_translate

        return None, None

    async def _process_translation_request(self, user_id: int, lang: str, text_to_translate: str, message: types.Message) -> bool:
        """Обрабатывает запрос перевода."""
        if lang not in translator.SUPPORTED_LANGUAGES:
            await message.reply(f"❌ Неподдерживаемый язык: {lang}\n"
                              f"Доступные: {', '.join(translator.SUPPORTED_LANGUAGES.keys())}")
            return True

        translation = translator.translate_text(text_to_translate, lang)

        if translation:
            await message.reply(translation, reply_markup=keyboard_manager.get_menu_button())
            log_info(f"Переведен текст на {lang}: {text_to_translate[:50]}...", user_id)

            # Логируем статистику в БД
            try:
                self.db.log_message(user_id, "translation", content=text_to_translate, response=translation)
                self.db.update_user_stats(user_id, "total_translations")
            except Exception as e:
                log_error(f"Ошибка логирования перевода пользователя {user_id}: {str(e)}")
        else:
            await message.reply("❌ Не удалось выполнить перевод.")
            log_error(f"Ошибка перевода текста: {text_to_translate}", user_id)

        return True

    def _is_math_expression(self, text: str) -> bool:
        """Проверяет, является ли текст математическим выражением."""
        # Удаляем пробелы
        text = text.replace(' ', '')

        # Проверяем на наличие цифр и математических операторов
        has_digits = any(c.isdigit() for c in text)
        has_operators = any(c in '+-*/^()' for c in text)

        return has_digits and has_operators and len(text) > 1

    async def _process_calc_request(self, user_id: int, expression: str, message: types.Message) -> bool:
        """Обрабатывает математический запрос."""
        result = calculator.calculate(expression)

        if result:
            await message.reply(f"🧮 <b>Результат:</b>\n\n{expression} = {result}", reply_markup=keyboard_manager.get_menu_button())
            log_info(f"Выполнен расчет: {expression} = {result}", user_id)

            # Логируем статистику в БД
            try:
                self.db.log_message(user_id, "calculator", content=expression, response=str(result))
                self.db.update_user_stats(user_id, "total_calculations")
            except Exception as e:
                log_error(f"Ошибка логирования калькулятора пользователя {user_id}: {str(e)}")
        else:
            await message.reply("❌ Не удалось вычислить выражение. Попробуйте другое.", reply_markup=keyboard_manager.get_menu_button())
            log_error(f"Ошибка вычисления: {expression}", user_id)

        return True

    async def _process_fun_request(self, user_id: int, text: str, message: types.Message) -> bool:
        """Обрабатывает запрос фактов/шуток/цитат."""
        text_lower = text.lower()

        if 'шутка' in text_lower or 'joke' in text_lower:
            joke = fun_service.get_random_joke()
            await message.reply(f"😂 <b>Шутка:</b>\n\n{joke}", reply_markup=keyboard_manager.get_menu_button())
            log_info("Отправлена шутка", user_id)

            # Логируем статистику в БД
            try:
                self.db.log_message(user_id, "joke", response=joke)
                self.db.update_user_stats(user_id, "total_jokes")
            except Exception as e:
                log_error(f"Ошибка логирования шутки пользователя {user_id}: {str(e)}")

        elif 'факт' in text_lower or 'fact' in text_lower:
            fact = fun_service.get_random_fact()
            await message.reply(f"🧠 <b>Интересный факт:</b>\n\n{fact}", reply_markup=keyboard_manager.get_menu_button())
            log_info("Отправлен факт", user_id)

            # Логируем статистику в БД
            try:
                self.db.log_message(user_id, "fact", response=fact)
                self.db.update_user_stats(user_id, "total_facts")
            except Exception as e:
                log_error(f"Ошибка логирования факта пользователя {user_id}: {str(e)}")

        elif 'цитата' in text_lower or 'quote' in text_lower:
            quote = fun_service.get_random_quote()
            await message.reply(f"💭 <b>Цитата:</b>\n\n{quote}", reply_markup=keyboard_manager.get_menu_button())
            log_info("Отправлена цитата", user_id)

            # Логируем статистику в БД
            try:
                self.db.log_message(user_id, "quote", response=quote)
                self.db.update_user_stats(user_id, "total_quotes")
            except Exception as e:
                log_error(f"Ошибка логирования цитаты пользователя {user_id}: {str(e)}")

        else:
            # По умолчанию отправляем факт
            fact = fun_service.get_random_fact()
            await message.reply(f"🧠 <b>Интересный факт:</b>\n\n{fact}", reply_markup=keyboard_manager.get_menu_button())
            log_info("Отправлен факт", user_id)

        return True

    async def handle_photo_message(self, message: types.Message):
        """Обработчик сообщений с изображениями."""
        user_id = message.from_user.id
        log_info("Получено сообщение с изображением", user_id)

        # Отправляем индикатор "загружает фото"
        await message.bot.send_chat_action(message.chat.id, "upload_photo")

        try:
            # Получаем самое большое изображение
            photo = message.photo[-1]

            # Проверяем размер файла
            if photo.file_size > config.MAX_FILE_SIZE:
                await message.reply("❌ Файл слишком большой. Максимальный размер: 20MB")
                return

            # Скачиваем изображение
            file_info = await message.bot.get_file(photo.file_id)
            image_data = await message.bot.download_file(file_info.file_path)

            # Анализируем изображение
            prompt = "Опиши это изображение подробно на русском языке. Что на нем изображено?"

            # Если есть подпись к изображению, используем её как промпт
            if message.caption:
                prompt = message.caption

            response = gemini_client.analyze_image(image_data.read(), prompt)

            if response:
                await message.reply(response)
                log_info("Отправлен анализ изображения", user_id)
            else:
                await message.reply("❌ Не удалось проанализировать изображение. Попробуйте другое фото.")
                log_error("Не удалось проанализировать изображение", user_id)

        except Exception as e:
            log_error(f"Ошибка при обработке изображения: {str(e)}", user_id, e)
            await message.reply("❌ Произошла ошибка при обработке изображения.")

    async def handle_voice_message(self, message: types.Message):
        """Обработчик голосовых сообщений."""
        user_id = message.from_user.id
        log_info("Получено голосовое сообщение", user_id)

        # Отправляем индикатор "загружает голосовое сообщение"
        await message.bot.send_chat_action(message.chat.id, "record_voice")

        try:
            # Проверяем размер файла
            if message.voice.file_size > config.MAX_FILE_SIZE:
                await message.reply("❌ Файл слишком большой. Максимальный размер: 20MB")
                return

            # Скачиваем голосовое сообщение
            file_info = await message.bot.get_file(message.voice.file_id)
            audio_data = await message.bot.download_file(file_info.file_path)

            # Распознаем текст через Gemini API
            recognized_text = gemini_client.transcribe_audio_with_gemini(audio_data.read())

            if recognized_text:
                log_info(f"Распознан текст из голосового через Gemini: {recognized_text[:100]}...", user_id)

                # Отправляем распознанный текст пользователю
                await message.reply(f"🎵 <i>Распознанный текст:</i> {recognized_text}")

                # Генерируем ответ через Gemini
                response = gemini_client.generate_text_response(recognized_text)

                if response:
                    await message.reply(response)
                    log_info("Отправлен ответ на голосовое сообщение", user_id)
                else:
                    await message.reply("❌ Не удалось обработать распознанный текст.")
                    log_error("Не удалось сгенерировать ответ на голосовое сообщение", user_id)
            else:
                await message.reply("❌ Не удалось распознать текст в голосовом сообщении. Попробуйте говорить четче или отправьте текстовое сообщение.")
                log_error("Не удалось распознать текст в голосовом сообщении", user_id)

        except Exception as e:
            log_error(f"Ошибка при обработке голосового сообщения: {str(e)}", user_id, e)
            await message.reply("❌ Произошла ошибка при обработке голосового сообщения.")

    async def handle_audio_message(self, message: types.Message):
        """Обработчик аудио файлов."""
        user_id = message.from_user.id
        log_info("Получен аудио файл", user_id)

        # Отправляем индикатор "загружает аудио"
        await message.bot.send_chat_action(message.chat.id, "upload_voice")

        try:
            # Проверяем размер файла
            if message.audio.file_size > config.MAX_FILE_SIZE:
                await message.reply("❌ Файл слишком большой. Максимальный размер: 20MB")
                return

            # Скачиваем аудио файл
            file_info = await message.bot.get_file(message.audio.file_id)
            audio_data = await message.bot.download_file(file_info.file_path)

            # Определяем MIME-тип на основе расширения файла
            mime_type = "audio/mpeg"  # по умолчанию
            if hasattr(message.audio, 'file_name') and message.audio.file_name:
                if message.audio.file_name.lower().endswith('.ogg'):
                    mime_type = "audio/ogg"
                elif message.audio.file_name.lower().endswith('.mp3'):
                    mime_type = "audio/mpeg"
                elif message.audio.file_name.lower().endswith('.wav'):
                    mime_type = "audio/wav"

            # Распознаем текст через Gemini API
            recognized_text = gemini_client.transcribe_audio_with_gemini(audio_data.read(), mime_type)

            if recognized_text:
                log_info(f"Распознан текст из аудио файла через Gemini: {recognized_text[:100]}...", user_id)

                # Отправляем распознанный текст пользователю
                await message.reply(f"🎵 <i>Распознанный текст:</i> {recognized_text}")

                # Генерируем ответ через Gemini
                response = gemini_client.generate_text_response(recognized_text)

                if response:
                    await message.reply(response)
                    log_info("Отправлен ответ на аудио файл", user_id)
                else:
                    await message.reply("❌ Не удалось обработать распознанный текст.")
                    log_error("Не удалось сгенерировать ответ на аудио файл", user_id)
            else:
                await message.reply("❌ Не удалось распознать текст в аудио файле. Попробуйте другой формат файла.")
                log_error("Не удалось распознать текст в аудио файле", user_id)

        except Exception as e:
            log_error(f"Ошибка при обработке аудио файла: {str(e)}", user_id, e)
            await message.reply("❌ Произошла ошибка при обработке аудио файла.")

    async def start_polling(self):
        """Запускает бота в режиме polling."""
        log_info("Запуск бота в режиме polling")
        await self.dp.start_polling(self.bot)

    async def stop(self):
        """Останавливает бота."""
        log_info("Остановка бота")
        await self.bot.session.close()


# Создаем глобальный экземпляр бота
ai_bot = AIBot()
