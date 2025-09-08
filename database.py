"""
Модуль для работы с базой данных PostgreSQL.
Содержит модели данных и функции для работы со статистикой пользователей.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, Boolean, BigInteger, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from sqlalchemy import and_, or_
from logger import log_info, log_error

Base = declarative_base()

class User(Base):
    """Модель пользователя."""
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)  # Telegram user ID
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), nullable=True)
    is_premium = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    # Статистика
    total_messages = Column(Integer, default=0)
    total_games = Column(Integer, default=0)
    total_facts = Column(Integer, default=0)
    total_jokes = Column(Integer, default=0)
    total_quotes = Column(Integer, default=0)
    total_calculations = Column(Integer, default=0)
    total_translations = Column(Integer, default=0)
    total_rps_games = Column(Integer, default=0)
    total_weather_requests = Column(Integer, default=0)

    # Время
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    banned_until = Column(DateTime, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать пользователя в словарь."""
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "language_code": self.language_code,
            "is_premium": self.is_premium,
            "is_admin": self.is_admin,
            "total_messages": self.total_messages,
            "total_games": self.total_games,
            "total_facts": self.total_facts,
            "total_jokes": self.total_jokes,
            "total_quotes": self.total_quotes,
            "total_calculations": self.total_calculations,
            "total_translations": self.total_translations,
            "total_rps_games": self.total_rps_games,
            "total_weather_requests": self.total_weather_requests,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "banned_until": self.banned_until.isoformat() if self.banned_until else None
        }

class GameSession(Base):
    """Модель игровой сессии."""
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, index=True)
    game_type = Column(String(50))  # guess_number, rps, quiz, magic_ball
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    result = Column(String(50), nullable=True)  # win, lose, draw
    score = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    game_data = Column(JSON, nullable=True)  # Дополнительные данные игры

class MessageLog(Base):
    """Модель для логирования сообщений."""
    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, index=True)
    message_type = Column(String(50))  # text, photo, voice, game, tool
    content = Column(Text, nullable=True)
    response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Float, nullable=True)  # Время обработки в секундах

class UserSettings(Base):
    """Модель настроек пользователя."""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, index=True)
    current_persona = Column(String(50), default="Дружелюбный помощник")
    notifications_enabled = Column(Boolean, default=True)
    language = Column(String(10), default="ru")
    timezone = Column(String(50), default="Asia/Tashkent")
    settings_data = Column(JSON, nullable=True)  # Дополнительные настройки

class SystemStats(Base):
    """Модель системной статистики."""
    __tablename__ = "system_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stat_type = Column(String(100))  # total_users, total_messages, etc.
    value = Column(BigInteger, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DatabaseManager:
    """Менеджер базы данных."""

    def __init__(self, database_url: str):
        """Инициализация подключения к БД."""
        try:
            self.engine = create_engine(database_url, pool_pre_ping=True)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

            # Создаем таблицы если они не существуют
            Base.metadata.create_all(bind=self.engine)

            log_info("Подключение к базе данных установлено")
        except Exception as e:
            log_error(f"Ошибка подключения к базе данных: {str(e)}")
            raise

    def get_session(self) -> Session:
        """Получить сессию базы данных."""
        return self.SessionLocal()

    def close(self):
        """Закрыть соединение с БД."""
        self.engine.dispose()

    # Методы для работы с пользователями

    def get_or_create_user(self, user_id: int, **user_data) -> User:
        """Получить или создать пользователя."""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                user = User(id=user_id, **user_data)
                session.add(user)
                session.commit()
                log_info(f"Создан новый пользователь: {user_id}")
            else:
                # Обновляем данные пользователя
                for key, value in user_data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                user.last_active = datetime.utcnow()
                session.commit()
            return user

    def update_user_stats(self, user_id: int, stat_type: str, increment: int = 1):
        """Обновить статистику пользователя."""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                if hasattr(user, stat_type):
                    current_value = getattr(user, stat_type) or 0
                    setattr(user, stat_type, current_value + increment)
                    session.commit()

    def get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить статистику пользователя."""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                return user.to_dict()
            return None

    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Получить всех пользователей с пагинацией."""
        with self.get_session() as session:
            users = session.query(User).order_by(User.last_active.desc()).limit(limit).offset(offset).all()
            return [user.to_dict() for user in users]

    def search_users(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Умный поиск пользователей."""
        with self.get_session() as session:
            # Ищем по ID, username, first_name, last_name
            users = session.query(User).filter(
                or_(
                    User.id == int(query) if query.isdigit() else False,
                    User.username.ilike(f"%{query}%"),
                    User.first_name.ilike(f"%{query}%"),
                    User.last_name.ilike(f"%{query}%")
                )
            ).limit(limit).all()
            return [user.to_dict() for user in users]

    def clear_user_stats(self, user_id: int):
        """Очистить статистику пользователя."""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.total_messages = 0
                user.total_games = 0
                user.total_facts = 0
                user.total_jokes = 0
                user.total_quotes = 0
                user.total_calculations = 0
                user.total_translations = 0
                user.total_rps_games = 0
                user.total_weather_requests = 0
                session.commit()

                # Удаляем связанные записи
                session.query(GameSession).filter(GameSession.user_id == user_id).delete()
                session.query(MessageLog).filter(MessageLog.user_id == user_id).delete()
                session.query(UserSettings).filter(UserSettings.user_id == user_id).delete()
                session.commit()

                log_info(f"Статистика пользователя {user_id} очищена")

    def clear_all_users_stats(self):
        """Очистить статистику всех пользователей."""
        with self.get_session() as session:
            # Сбрасываем счетчики пользователей
            session.query(User).update({
                User.total_messages: 0,
                User.total_games: 0,
                User.total_facts: 0,
                User.total_jokes: 0,
                User.total_quotes: 0,
                User.total_calculations: 0,
                User.total_translations: 0,
                User.total_rps_games: 0,
                User.total_weather_requests: 0
            })

            # Удаляем все связанные записи
            session.query(GameSession).delete()
            session.query(MessageLog).delete()
            session.query(UserSettings).delete()
            session.commit()

            log_info("Статистика всех пользователей очищена")

    def ban_user(self, user_id: int, ban_duration_hours: int = 24):
        """Забанить пользователя."""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.banned_until = datetime.utcnow() + timedelta(hours=ban_duration_hours)
                session.commit()
                log_info(f"Пользователь {user_id} забанен на {ban_duration_hours} часов")

    def unban_user(self, user_id: int):
        """Разбанить пользователя."""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.banned_until = None
                session.commit()
                log_info(f"Пользователь {user_id} разбанен")

    def is_user_banned(self, user_id: int) -> bool:
        """Проверить, забанен ли пользователь."""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user and user.banned_until:
                if user.banned_until > datetime.utcnow():
                    return True
                else:
                    # Бан истек, снимаем
                    user.banned_until = None
                    session.commit()
            return False

    # Методы для работы с играми

    def start_game_session(self, user_id: int, game_type: str, game_data: Dict = None) -> int:
        """Начать игровую сессию."""
        with self.get_session() as session:
            game_session = GameSession(
                user_id=user_id,
                game_type=game_type,
                game_data=game_data or {}
            )
            session.add(game_session)
            session.commit()
            return game_session.id

    def end_game_session(self, session_id: int, result: str, score: int = 0, attempts: int = 0):
        """Завершить игровую сессию."""
        with self.get_session() as session:
            game_session = session.query(GameSession).filter(GameSession.id == session_id).first()
            if game_session:
                game_session.finished_at = datetime.utcnow()
                game_session.result = result
                game_session.score = score
                game_session.attempts = attempts
                session.commit()

    def get_user_game_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику игр пользователя."""
        with self.get_session() as session:
            stats = session.query(
                GameSession.game_type,
                func.count(GameSession.id).label('total_games'),
                func.avg(GameSession.score).label('avg_score'),
                func.sum(GameSession.attempts).label('total_attempts')
            ).filter(
                and_(
                    GameSession.user_id == user_id,
                    GameSession.finished_at.isnot(None)
                )
            ).group_by(GameSession.game_type).all()

            result = {}
            for stat in stats:
                result[stat.game_type] = {
                    'total_games': stat.total_games,
                    'avg_score': float(stat.avg_score) if stat.avg_score else 0,
                    'total_attempts': stat.total_attempts or 0
                }
            return result

    # Методы для работы с сообщениями

    def log_message(self, user_id: int, message_type: str, content: str = None,
                   response: str = None, processing_time: float = None):
        """Залогировать сообщение."""
        with self.get_session() as session:
            message_log = MessageLog(
                user_id=user_id,
                message_type=message_type,
                content=content,
                response=response,
                processing_time=processing_time
            )
            session.add(message_log)
            session.commit()

    # Системная статистика

    def get_system_stats(self) -> Dict[str, Any]:
        """Получить системную статистику."""
        with self.get_session() as session:
            total_users = session.query(func.count(User.id)).scalar()
            total_messages = session.query(func.count(MessageLog.id)).scalar()
            total_games = session.query(func.count(GameSession.id)).scalar()

            # Статистика по типам сообщений
            message_stats = session.query(
                MessageLog.message_type,
                func.count(MessageLog.id)
            ).group_by(MessageLog.message_type).all()

            message_type_stats = {stat[0]: stat[1] for stat in message_stats}

            return {
                'total_users': total_users or 0,
                'total_messages': total_messages or 0,
                'total_games': total_games or 0,
                'message_types': message_type_stats
            }

    def update_system_stats(self, stat_type: str, increment: int = 1):
        """Обновить системную статистику."""
        with self.get_session() as session:
            stat = session.query(SystemStats).filter(SystemStats.stat_type == stat_type).first()
            if not stat:
                stat = SystemStats(stat_type=stat_type, value=increment)
                session.add(stat)
            else:
                stat.value += increment
            session.commit()

# Глобальный экземпляр менеджера БД
db_manager = None

def init_database(database_url: str) -> DatabaseManager:
    """Инициализировать подключение к базе данных."""
    global db_manager
    db_manager = DatabaseManager(database_url)
    return db_manager

def get_db_manager() -> DatabaseManager:
    """Получить экземпляр менеджера БД."""
    return db_manager
