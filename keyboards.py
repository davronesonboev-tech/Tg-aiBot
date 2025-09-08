"""
Модуль для создания интерактивных клавиатур (кнопок) в Telegram боте.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from personas import persona_manager, PersonaType


class KeyboardManager:
    """Менеджер клавиатур для бота."""

    @staticmethod
    def get_main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
        """Главная клавиатура с основными функциями."""
        builder = InlineKeyboardBuilder()

        # Основные категории
        builder.button(text="🎭 Режимы общения", callback_data="menu_personas")
        builder.button(text="🎮 Игры", callback_data="menu_games")
        builder.button(text="🛠️ Инструменты", callback_data="menu_tools")

        # Служебные функции
        builder.button(text="📊 Статистика", callback_data="stats")
        builder.button(text="🧠 Очистить память", callback_data="clear_memory")
        builder.button(text="❓ Помощь", callback_data="help")

        # Админ-панель (только для админа)
        if is_admin:
            builder.button(text="👑 Админ", callback_data="admin_panel")

        # Устанавливаем сетку 2x2 для основных кнопок, затем 3x3 для остальных
        if is_admin:
            builder.adjust(2, 3, 1)
        else:
            builder.adjust(2, 3, 1)

        return builder.as_markup()

    @staticmethod
    def get_personas_menu() -> InlineKeyboardMarkup:
        """Меню выбора режима общения."""
        builder = InlineKeyboardBuilder()

        # Получаем все доступные персоны
        personas = persona_manager.get_all_personas()

        for persona_type, persona in personas.items():
            emoji_map = {
                PersonaType.FRIENDLY: "🤗",
                PersonaType.PROGRAMMER: "💻",
                PersonaType.EXPERT: "🎓",
                PersonaType.CREATIVE: "🎨",
                PersonaType.PROFESSIONAL: "💼"
            }

            emoji = emoji_map.get(persona_type, "🎭")
            builder.button(
                text=f"{emoji} {persona.name}",
                callback_data=f"persona_{persona_type.value}"
            )

        # Кнопка назад
        builder.button(text="⬅️ Назад", callback_data="back_to_main")

        builder.adjust(1)  # Все кнопки в один столбец

        return builder.as_markup()

    @staticmethod
    def get_games_menu() -> InlineKeyboardMarkup:
        """Меню игр."""
        builder = InlineKeyboardBuilder()

        builder.button(text="🪨 Камень-Ножницы-Бумага", callback_data="game_rps")
        builder.button(text="🎲 Кости", callback_data="game_dice")
        builder.button(text="🔢 Угадай число", callback_data="game_guess")
        builder.button(text="🧠 Викторина", callback_data="game_quiz")
        builder.button(text="🎱 Волшебный шар", callback_data="game_ball")

        builder.button(text="⬅️ Назад", callback_data="back_to_main")

        builder.adjust(1)

        return builder.as_markup()

    @staticmethod
    def get_rps_choice_menu() -> InlineKeyboardMarkup:
        """Клавиатура выбора для игры камень-ножницы-бумага."""
        builder = InlineKeyboardBuilder()

        builder.button(text="🪨 Камень", callback_data="rps_rock")
        builder.button(text="✂️ Ножницы", callback_data="rps_scissors")
        builder.button(text="📄 Бумага", callback_data="rps_paper")

        builder.button(text="⬅️ Назад в игры", callback_data="menu_games")

        builder.adjust(3, 1)
        return builder.as_markup()

    @staticmethod
    def get_tools_menu() -> InlineKeyboardMarkup:
        """Меню инструментов."""
        builder = InlineKeyboardBuilder()

        builder.button(text="🧮 Калькулятор", callback_data="tool_calc")
        builder.button(text="🌤️ Погода", callback_data="tool_weather")
        builder.button(text="🌐 Переводчик", callback_data="tool_translate")
        builder.button(text="🤣 Шутка", callback_data="fun_joke")
        builder.button(text="💡 Цитата", callback_data="fun_quote")
        builder.button(text="🤓 Факт", callback_data="fun_fact")

        builder.button(text="⬅️ Назад", callback_data="back_to_main")

        builder.adjust(2)

        return builder.as_markup()

    @staticmethod
    def get_dice_bet_menu() -> InlineKeyboardMarkup:
        """Меню выбора ставки для игры в кости."""
        builder = InlineKeyboardBuilder()

        builder.button(text="🎯 Низкая ставка", callback_data="dice_low")
        builder.button(text="🎲 Средняя ставка", callback_data="dice_medium")
        builder.button(text="💎 Высокая ставка", callback_data="dice_high")

        builder.button(text="⬅️ Назад", callback_data="menu_games")

        builder.adjust(1)

        return builder.as_markup()

    @staticmethod
    def get_guess_difficulty_menu() -> InlineKeyboardMarkup:
        """Меню выбора сложности для игры угадай число."""
        builder = InlineKeyboardBuilder()

        builder.button(text="🐣 Легко (1-10)", callback_data="guess_easy")
        builder.button(text="🎯 Средне (1-100)", callback_data="guess_medium")
        builder.button(text="🔥 Сложно (1-1000)", callback_data="guess_hard")

        builder.button(text="⬅️ Назад", callback_data="menu_games")

        builder.adjust(1)

        return builder.as_markup()

    @staticmethod
    def get_rps_menu() -> InlineKeyboardMarkup:
        """Меню выбора для игры камень-ножницы-бумага."""
        builder = InlineKeyboardBuilder()

        builder.button(text="🪨 Камень", callback_data="rps_камень")
        builder.button(text="✂️ Ножницы", callback_data="rps_ножницы")
        builder.button(text="📄 Бумага", callback_data="rps_бумага")

        builder.button(text="⬅️ Назад", callback_data="menu_games")

        builder.adjust(3, 1)  # 3 кнопки выбора, затем назад

        return builder.as_markup()

    @staticmethod
    def get_calc_menu() -> InlineKeyboardMarkup:
        """Клавиатура калькулятора."""
        builder = InlineKeyboardBuilder()

        # Цифры
        for i in range(7, 10):
            builder.button(text=str(i), callback_data=f"calc_{i}")
        builder.button(text="➗", callback_data="calc_/")

        for i in range(4, 7):
            builder.button(text=str(i), callback_data=f"calc_{i}")
        builder.button(text="✖️", callback_data="calc_*")

        for i in range(1, 4):
            builder.button(text=str(i), callback_data=f"calc_{i}")
        builder.button(text="➖", callback_data="calc_-")

        builder.button(text="0", callback_data="calc_0")
        builder.button(text=".", callback_data="calc_.")
        builder.button(text="=", callback_data="calc_=")
        builder.button(text="➕", callback_data="calc_+")

        builder.button(text="⬅️ Очистить", callback_data="calc_clear")
        builder.button(text="✅ Вычислить", callback_data="calc_calculate")

        builder.adjust(4, 4, 4, 2)

        return builder.as_markup()

    @staticmethod
    def get_uzbekistan_weather_menu() -> InlineKeyboardMarkup:
        """Меню выбора областей Узбекистана для погоды."""
        builder = InlineKeyboardBuilder()

        # Области Узбекистана
        regions = [
            ("🏛️ Ташкент", "weather_tashkent"),
            ("🌾 Андижан", "weather_andijan"),
            ("🏺 Бухара", "weather_bukhara"),
            ("🌾 Джизак", "weather_jizzakh"),
            ("🏜️ Каракалпакстан", "weather_karakalpakstan"),
            ("🌾 Кашкадарья", "weather_kashkadarya"),
            ("🏭 Наманган", "weather_namangan"),
            ("⛏️ Навои", "weather_navoi"),
            ("🏺 Самарканд", "weather_samarkand"),
            ("🌾 Сурхандарья", "weather_surkhondarya"),
            ("🌾 Сырдарья", "weather_syrdarya"),
            ("🌾 Ташкентская обл.", "weather_tashkent_region"),
            ("🌾 Фергана", "weather_fergana"),
            ("🏺 Хорезм", "weather_khorezm")
        ]

        for region_name, callback_data in regions:
            builder.button(text=region_name, callback_data=callback_data)

        # Кнопка назад
        builder.button(text="⬅️ Назад", callback_data="menu_tools")

        builder.adjust(2)  # 2 колонки для областей
        return builder.as_markup()

    @staticmethod
    def get_translation_languages_menu() -> InlineKeyboardMarkup:
        """Меню выбора языков для перевода."""
        builder = InlineKeyboardBuilder()

        # Языки для перевода
        languages = [
            ("🇺🇿 Узбекский", "lang_uz"),
            ("🇷🇺 Русский", "lang_ru"),
            ("🇺🇸 Английский", "lang_en"),
            ("🇪🇸 Испанский", "lang_es"),
            ("🇫🇷 Французский", "lang_fr"),
            ("🇩🇪 Немецкий", "lang_de"),
            ("🇮🇹 Итальянский", "lang_it"),
            ("🇵🇹 Португальский", "lang_pt"),
            ("🇨🇳 Китайский", "lang_zh"),
            ("🇯🇵 Японский", "lang_ja"),
            ("🇰🇷 Корейский", "lang_ko")
        ]

        for lang_name, callback_data in languages:
            builder.button(text=lang_name, callback_data=callback_data)

        # Кнопка назад
        builder.button(text="⬅️ Назад", callback_data="menu_tools")

        builder.adjust(3, 3, 3, 2)  # 3 колонки для языков
        return builder.as_markup()

    @staticmethod
    def get_menu_button() -> InlineKeyboardMarkup:
        """Кнопка для быстрого доступа к главному меню."""
        builder = InlineKeyboardBuilder()

        builder.button(text="🏠 Меню", callback_data="show_main_menu")

        return builder.as_markup()

    @staticmethod
    def get_admin_menu() -> InlineKeyboardMarkup:
        """Админ-панель для управления ботом."""
        builder = InlineKeyboardBuilder()

        builder.button(text="👥 Пользователи", callback_data="admin_users")
        builder.button(text="📊 Статистика", callback_data="admin_stats")
        builder.button(text="🔍 Поиск", callback_data="admin_search")
        builder.button(text="🚫 Баны", callback_data="admin_bans")

        builder.button(text="⬅️ Назад", callback_data="back_to_main")

        builder.adjust(2, 2, 1)
        return builder.as_markup()

    @staticmethod
    def get_admin_users_menu() -> InlineKeyboardMarkup:
        """Меню управления пользователями."""
        builder = InlineKeyboardBuilder()

        builder.button(text="📋 Список пользователей", callback_data="admin_users_list")
        builder.button(text="🧹 Очистить одного", callback_data="admin_clear_user")
        builder.button(text="🗑️ Очистить всех", callback_data="admin_clear_all")
        builder.button(text="🚫 Забанить", callback_data="admin_ban_user")
        builder.button(text="✅ Разбанить", callback_data="admin_unban_user")

        builder.button(text="⬅️ Назад в админку", callback_data="admin_main")

        builder.adjust(2, 2, 1)
        return builder.as_markup()

    @staticmethod
    def get_admin_stats_menu() -> InlineKeyboardMarkup:
        """Меню просмотра статистики."""
        builder = InlineKeyboardBuilder()

        builder.button(text="📊 Общая статистика", callback_data="admin_stats_general")
        builder.button(text="🎮 Статистика игр", callback_data="admin_stats_games")
        builder.button(text="💬 Статистика сообщений", callback_data="admin_stats_messages")
        builder.button(text="📈 Графики и тренды", callback_data="admin_stats_charts")

        builder.button(text="⬅️ Назад в админку", callback_data="admin_main")

        builder.adjust(1, 1, 1, 1, 1)
        return builder.as_markup()

    @staticmethod
    def get_admin_search_menu() -> InlineKeyboardMarkup:
        """Меню поиска пользователей."""
        builder = InlineKeyboardBuilder()

        builder.button(text="🔍 Поиск по ID", callback_data="admin_search_id")
        builder.button(text="👤 Поиск по username", callback_data="admin_search_username")
        builder.button(text="📝 Поиск по имени", callback_data="admin_search_name")
        builder.button(text="📊 Топ активных", callback_data="admin_top_users")

        builder.button(text="⬅️ Назад в админку", callback_data="admin_main")

        builder.adjust(2, 2, 1)
        return builder.as_markup()

    @staticmethod
    def get_confirmation_menu(action: str, callback_data: str) -> InlineKeyboardMarkup:
        """Меню подтверждения действия."""
        builder = InlineKeyboardBuilder()

        action_text = {
            "clear_memory": "очистить память",
            "reset_settings": "сбросить настройки"
        }.get(action, action)

        builder.button(text=f"✅ Подтвердить {action_text}", callback_data=callback_data)
        builder.button(text="❌ Отмена", callback_data="cancel")

        builder.adjust(1)

        return builder.as_markup()


# Создаем глобальный экземпляр менеджера клавиатур
keyboard_manager = KeyboardManager()
