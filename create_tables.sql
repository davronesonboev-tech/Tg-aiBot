Starting Container
🤖 Telegram AI Bot
==================================================
✅ Конфигурация загружена успешно
2025-09-14 17:57:10 - telegram_ai_bot - INFO - Подключение к базе данных...
2025-09-14 17:57:10 - telegram_ai_bot - INFO - Подключение к базе данных установлено
2025-09-14 17:57:10 - telegram_ai_bot - INFO - База данных инициализирована успешно
2025-09-14 17:57:10 - telegram_ai_bot - INFO - Запуск Telegram AI бота...
2025-09-14 17:57:13 - telegram_ai_bot - INFO - Загружены воспоминания для 0 пользователей
2025-09-14 17:57:13 - telegram_ai_bot - INFO - Бот успешно создан
2025-09-14 17:57:13 - telegram_ai_bot - INFO - Запуск бота в режиме polling
2025-09-14 17:57:27 - telegram_ai_bot - INFO - [User 1395804259] Получена команда /start
2025-09-14 17:57:27 - telegram_ai_bot - ERROR - Ошибка сохранения пользователя 1395804259: (psycopg2.errors.UndefinedColumn) column users.total_rps_games does not exist
LINE 1: ...s.total_translations AS users_total_translations, users.tota...
                                                             ^
[SQL: SELECT users.id AS users_id, users.username AS users_username, users.first_name AS users_first_name, users.last_name AS users_last_name, users.language_code AS users_language_code, users.is_premium AS users_is_premium, users.is_admin AS users_is_admin, users.total_messages AS users_total_messages, users.total_games AS users_total_games, users.total_facts AS users_total_facts, users.total_jokes AS users_total_jokes, users.total_quotes AS users_total_quotes, users.total_calculations AS users_total_calculations, users.total_translations AS users_total_translations, users.total_rps_games AS users_total_rps_games, users.total_quiz_games AS users_total_quiz_games, users.total_weather_requests AS users_total_weather_requests, users.created_at AS users_created_at, users.last_active AS users_last_active, users.banned_until AS users_banned_until 
FROM users 
WHERE users.id = %(id_1)s 
 LIMIT %(param_1)s]
[parameters: {'id_1': 1395804259, 'param_1': 1}]
(Background on this error at: https://sqlalche.me/e/20/f405)
2025-09-14 17:57:30 - telegram_ai_bot - INFO - [User 1395804259] Получен callback: menu_personas
2025-09-14 17:57:32 - telegram_ai_bot - INFO - [User 1395804259] Получен callback: persona_programmer
2025-09-14 17:57:32 - telegram_ai_bot - INFO - Создана новая память для пользователя 1395804259
2025-09-14 17:57:36 - telegram_ai_bot - INFO - [User 1395804259] Получено текстовое сообщение: Привет...
2025-09-14 17:57:36 - telegram_ai_bot - INFO - Добавлено сообщение в память пользователя 1395804259: user - Привет...
2025-09-14 17:57:36 - telegram_ai_bot - INFO - Генерация ответа на текстовый запрос: Контекст предыдущего разговора:
Пользователь: Привет
Текущее сообщение пользователя: Привет...
2025-09-14 17:57:36 - telegram_ai_bot - INFO - Отправка запроса к Gemini API: https://generativelanguage.googleapis.com/v1/models/gemini-2.5-pro:generateContent
2025-09-14 17:57:48 - telegram_ai_bot - INFO - Успешно получен ответ от Gemini API
2025-09-14 17:57:48 - telegram_ai_bot - INFO - [User 1395804259] Отправлен ответ на текстовое сообщение
2025-09-14 17:57:48 - telegram_ai_bot - ERROR - Ошибка логирования сообщения пользователя 1395804259: (psycopg2.errors.UndefinedColumn) column users.total_rps_games does not exist
LINE 1: ...s.total_translations AS users_total_translations, users.tota...
                                                             ^
[SQL: SELECT users.id AS users_id, users.username AS users_username, users.first_name AS users_first_name, users.last_name AS users_last_name, users.language_code AS users_language_code, users.is_premium AS users_is_premium, users.is_admin AS users_is_admin, users.total_messages AS users_total_messages, users.total_games AS users_total_games, users.total_facts AS users_total_facts, users.total_jokes AS users_total_jokes, users.total_quotes AS users_total_quotes, users.total_calculations AS users_total_calculations, users.total_translations AS users_total_translations, users.total_rps_games AS users_total_rps_games, users.total_quiz_games AS users_total_quiz_games, users.total_weather_requests AS users_total_weather_requests, users.created_at AS users_created_at, users.last_active AS users_last_active, users.banned_until AS users_banned_until 
FROM users 
WHERE users.id = %(id_1)s 
 LIMIT %(param_1)s]
[parameters: {'id_1': 1395804259, 'param_1': 1}]
(Background on this error at: https://sqlalche.me/e/20/f405)
2025-09-14 17:57:48 - telegram_ai_bot - INFO - Добавлено сообщение в память пользователя 1395804259: assistant - Привет! Рад снова быть на связи.
Я — ваш персонал...
2025-09-14 17:57:58 - telegram_ai_bot - INFO - [User 1395804259] Получен callback: show_main_menu
2025-09-14 17:58:00 - telegram_ai_bot - INFO - [User 1395804259] Получен callback: menu_games
2025-09-14 17:58:01 - telegram_ai_bot - INFO - [User 1395804259] Получен callback: game_quiz
2025-09-14 17:58:03 - telegram_ai_bot - INFO - [User 1395804259] Получен callback: quiz_select_industry
2025-09-14 17:58:05 - telegram_ai_bot - INFO - [User 1395804259] Получен callback: quiz_industry_программирование
2025-09-14 17:58:05 - telegram_ai_bot - ERROR - Ошибка при сохранении воспоминаний: Circular reference detected
2025-09-14 17:58:06 - telegram_ai_bot - INFO - [User 1395804259] Получен callback: quiz_select_count
2025-09-14 17:58:07 - telegram_ai_bot - INFO - [User 1395804259] Получен callback: quiz_count_10
2025-09-14 17:58:07 - telegram_ai_bot - ERROR - Ошибка при сохранении воспоминаний: Circular reference detected
2025-09-14 17:58:09 - telegram_ai_bot - INFO - [User 1395804259] Получен callback: quiz_start
2025-09-14 17:58:09 - telegram_ai_bot - ERROR - [User 1395804259] Ошибка при обработке callback quiz_start: cannot access local variable 'datetime' where it is not associated with a value
Traceback (most recent call last):
  File "/app/bot.py", line 1395, in handle_callback
    'start_time': datetime.now(),
                  ^^^^^^^^
UnboundLocalError: cannot access local variable 'datetime' where it is not associated with a value
