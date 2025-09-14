"""
Модуль для работы с базой данных PostgreSQL.
Содержит модели данных и функции для работы со статистикой пользователей.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, Boolean, BigInteger, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from sqlalchemy import and_, or_, desc, asc
from logger import log_info, log_error
import json

Base = declarative_base()

class User(Base):
    """Модель пользователя."""
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)  # Telegram user ID
    username = Column(String(255), nullable=True, index=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), nullable=True)
    is_premium = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)

    # Статистика
    total_messages = Column(Integer, default=0)
    total_ai_requests = Column(Integer, default=0)
    total_games = Column(Integer, default=0)
    total_facts = Column(Integer, default=0)
    total_jokes = Column(Integer, default=0)
    total_quotes = Column(Integer, default=0)
    total_calculations = Column(Integer, default=0)
    total_translations = Column(Integer, default=0)
    total_weather_requests = Column(Integer, default=0)
    total_image_analyses = Column(Integer, default=0)
    total_voice_messages = Column(Integer, default=0)
    total_documents_processed = Column(Integer, default=0)
    
    # Игровая статистика
    total_rps_games = Column(Integer, default=0)
    total_quiz_games = Column(Integer, default=0)
    total_guess_games = Column(Integer, default=0)
    total_dice_games = Column(Integer, default=0)
    total_magic_ball_questions = Column(Integer, default=0)
    
    # Метрики производительности и вовлеченности
    avg_response_time = Column(Float, default=0.0)
    total_session_time = Column(Integer, default=0)  # в секундах
    favorite_persona = Column(String(50), nullable=True)
    preferred_language = Column(String(10), default='ru')
    
    # Продвинутые настройки пользователя
    user_preferences = Column(JSON, nullable=True)
    interaction_patterns = Column(JSON, nullable=True)
    
    # Время
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_active = Column(DateTime, default=datetime.utcnow, index=True)
    banned_until = Column(DateTime, nullable=True)
    last_message_at = Column(DateTime, nullable=True)

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
            "is_banned": self.is_banned,
            "total_messages": self.total_messages,
            "total_ai_requests": self.total_ai_requests,
            "total_games": self.total_games,
            "total_facts": self.total_facts,
            "total_jokes": self.total_jokes,
            "total_quotes": self.total_quotes,
            "total_calculations": self.total_calculations,
            "total_translations": self.total_translations,
            "total_weather_requests": self.total_weather_requests,
            "total_image_analyses": self.total_image_analyses,
            "total_voice_messages": self.total_voice_messages,
            "total_documents_processed": self.total_documents_processed,
            "total_rps_games": self.total_rps_games,
            "total_quiz_games": self.total_quiz_games,
            "total_guess_games": self.total_guess_games,
            "total_dice_games": self.total_dice_games,
            "total_magic_ball_questions": self.total_magic_ball_questions,
            "avg_response_time": self.avg_response_time,
            "total_session_time": self.total_session_time,
            "favorite_persona": self.favorite_persona,
            "preferred_language": self.preferred_language,
            "user_preferences": self.user_preferences,
            "interaction_patterns": self.interaction_patterns,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "banned_until": self.banned_until.isoformat() if self.banned_until else None,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None
        }

class GameSession(Base):
    """Модель игровой сессии."""
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, index=True)
    game_type = Column(String(50), index=True)  # guess_number, rps, quiz, magic_ball, dice
    difficulty = Column(String(20), nullable=True)  # easy, medium, hard
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    finished_at = Column(DateTime, nullable=True)
    result = Column(String(50), nullable=True)  # win, lose, draw, completed
    score = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    duration_seconds = Column(Integer, nullable=True)
    
    # Улучшенное отслеживание данных игры
    game_data = Column(JSON, nullable=True)  # Подробная информация о игре
    user_choices = Column(JSON, nullable=True)  # Отслеживание выборов пользователя
    bot_responses = Column(JSON, nullable=True)  # Отслеживание ответов бота
    performance_metrics = Column(JSON, nullable=True)  # Скорость, точность и т.д.

class MessageLog(Base):
    """Модель для логирования сообщений."""
    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, index=True)
    message_type = Column(String(50), index=True)  # text, photo, voice, game, tool, ai_request
    content = Column(Text, nullable=True)
    response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    processing_time = Column(Float, nullable=True)  # Время в секундах
    
    # Улучшенное отслеживание сообщений
    tokens_used = Column(Integer, nullable=True)  # Для запросов к AI
    model_used = Column(String(100), nullable=True)  # Используемая модель AI
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    context_length = Column(Integer, nullable=True)
    
    # Метаданные сообщения
    message_metadata = Column(JSON, nullable=True)
    user_satisfaction = Column(Integer, nullable=True)  # Оценка от 1 до 5

class UserSettings(Base):
    """Модель настроек пользователя."""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, index=True)
    current_persona = Column(String(50), default="Дружелюбный помощник")
    notifications_enabled = Column(Boolean, default=True)
    language = Column(String(10), default="ru")
    timezone = Column(String(50), default="Asia/Tashkent")
    
    # Продвинутые настройки пользователя
    ai_creativity_level = Column(Float, default=0.7)  # 0.0 до 1.0
    response_length_preference = Column(String(20), default="medium")  # короткий, средний, длинный
    preferred_game_difficulty = Column(String(20), default="medium")
    auto_translate = Column(Boolean, default=False)
    voice_response_enabled = Column(Boolean, default=False)
    
    # Настройки UI и взаимодействия
    keyboard_style = Column(String(20), default="стандартный")  # стандартный, компактный, минималистичный
    show_tips = Column(Boolean, default=True)
    analytics_enabled = Column(Boolean, default=True)
    
    settings_data = Column(JSON, nullable=True)  # Дополнительные настройки
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SystemStats(Base):
    """Модель системной статистики."""
    __tablename__ = "system_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stat_type = Column(String(100), index=True)
    value = Column(BigInteger, default=0)
    system_metadata = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

class UserAnalytics(Base):
    """Новая модель для аналитики пользователей."""
    __tablename__ = "user_analytics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, index=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Ежедневные метрики активности
    daily_messages = Column(Integer, default=0)
    daily_ai_requests = Column(Integer, default=0)
    daily_games_played = Column(Integer, default=0)
    daily_session_time = Column(Integer, default=0)  # секунды
    
    # Метрики вовлеченности
    unique_features_used = Column(JSON, nullable=True)  # Список использованных функций
    peak_activity_hour = Column(Integer, nullable=True)  # 0-23
    interaction_quality_score = Column(Float, nullable=True)  # 0.0-1.0
    
    # Метрики производительности
    avg_response_satisfaction = Column(Float, nullable=True)
    error_rate = Column(Float, nullable=True)
    
    analytics_data = Column(JSON, nullable=True)

class PerformanceMetrics(Base):
    """Новая модель для метрик производительности."""
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Отслеживание производительности системы
    total_active_users = Column(Integer, default=0)
    avg_response_time = Column(Float, default=0.0)
    total_requests_per_hour = Column(Integer, default=0)
    error_rate = Column(Float, default=0.0)
    
    # Производительность моделей AI
    ai_model_used = Column(String(100), nullable=True)
    avg_tokens_per_request = Column(Float, default=0.0)
    ai_success_rate = Column(Float, default=0.0)
    
    # Использование ресурсов
    memory_usage_mb = Column(Float, nullable=True)
    cpu_usage_percent = Column(Float, nullable=True)
    
    metrics_data = Column(JSON, nullable=True)

# Добавление индексов для улучшенной производительности
Index('idx_user_last_active', User.last_active)
Index('idx_user_created_at', User.created_at)
Index('idx_message_log_created_at', MessageLog.created_at)
Index('idx_game_session_started_at', GameSession.started_at)
Index('idx_user_analytics_date', UserAnalytics.date)
Index('idx_performance_metrics_timestamp', PerformanceMetrics.timestamp)

class EnhancedDatabaseManager:
    """Улучшенный менеджер базы данных с расширенными возможностями."""

    def __init__(self, database_url: str):
        """Инициализация подключения к БД."""
        try:
            # Улучшенное подключение с лучшей конфигурацией
            self.engine = create_engine(
                database_url, 
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
                echo=False  # Установите True для отладки SQL
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

            # Создаем таблицы если они не существуют
            Base.metadata.create_all(bind=self.engine)

            log_info("Подключение к улучшенной базе данных установлено")
        except Exception as e:
            log_error(f"Ошибка подключения к базе данных: {str(e)}")
            raise

    def get_session(self) -> Session:
        """Получить сессию базы данных."""
        return self.SessionLocal()

    def close(self):
        """Закрыть соединение с БД."""
        self.engine.dispose()

    # Улучшенные методы управления пользователями
    def get_or_create_user(self, user_id: int, **user_data) -> User:
        """Получить или создать пользователя с улучшенным отслеживанием."""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                user = User(id=user_id, **user_data)
                session.add(user)
                session.commit()
                log_info(f"Создан новый пользователь: {user_id}")
                
                # Создание настроек по умолчанию для нового пользователя
                self._create_default_user_settings(user_id)
                
                # Логирование события создания пользователя
                self._log_system_event("user_created", {"user_id": user_id})
            else:
                # Обновляем данные пользователя
                for key, value in user_data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                user.last_active = datetime.utcnow()
                user.last_message_at = datetime.utcnow()
                session.commit()
            return user

    def _create_default_user_settings(self, user_id: int):
        """Создает настройки по умолчанию для нового пользователя."""
        with self.get_session() as session:
            settings = UserSettings(user_id=user_id)
            session.add(settings)
            session.commit()

    def _log_system_event(self, event_type: str, data: Dict[str, Any]):
        """Логирует системные события."""
        try:
            with self.get_session() as session:
                stat = SystemStats(
                    stat_type=f"event_{event_type}",
                    value=1,
                    system_metadata=data
                )
                session.add(stat)
                session.commit()
        except Exception as e:
            log_error(f"Ошибка логирования системного события: {str(e)}")

    # Улучшенные методы статистики
    def update_user_stats(self, user_id: int, stat_type: str, increment: int = 1, **kwargs):
        """Обновить статистику пользователя с дополнительными метриками."""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                if hasattr(user, stat_type):
                    current_value = getattr(user, stat_type) or 0
                    setattr(user, stat_type, current_value + increment)
                    
                    # Обновление паттернов взаимодействия
                    self._update_interaction_patterns(user, stat_type, kwargs)
                    
                    session.commit()
                    
                    # Обновление ежедневной аналитики
                    self._update_daily_analytics(user_id, stat_type, increment)

    def _update_interaction_patterns(self, user: User, stat_type: str, metadata: Dict):
        """Обновляет паттерны взаимодействия пользователя."""
        try:
            patterns = user.interaction_patterns or {}
            
            # Отслеживание использования функций
            if 'features_used' not in patterns:
                patterns['features_used'] = {}
            
            feature_category = self._get_feature_category(stat_type)
            patterns['features_used'][feature_category] = patterns['features_used'].get(feature_category, 0) + 1
            
            # Отслеживание паттернов времени
            current_hour = datetime.utcnow().hour
            if 'hourly_activity' not in patterns:
                patterns['hourly_activity'] = {}
            patterns['hourly_activity'][str(current_hour)] = patterns['hourly_activity'].get(str(current_hour), 0) + 1
            
            user.interaction_patterns = patterns
        except Exception as e:
            log_error(f"Ошибка обновления паттернов взаимодействия: {str(e)}")

    def _get_feature_category(self, stat_type: str) -> str:
        """Определяет категорию функции по типу статистики."""
        categories = {
            'total_messages': 'communication',
            'total_ai_requests': 'ai_interaction',
            'total_games': 'entertainment',
            'total_calculations': 'tools',
            'total_translations': 'tools',
            'total_weather_requests': 'tools',
            'total_image_analyses': 'ai_interaction',
            'total_voice_messages': 'communication'
        }
        return categories.get(stat_type, 'other')

    def _update_daily_analytics(self, user_id: int, stat_type: str, increment: int):
        """Обновляет ежедневную аналитику пользователя."""
        try:
            with self.get_session() as session:
                today = datetime.utcnow().date()
                analytics = session.query(UserAnalytics).filter(
                    and_(
                        UserAnalytics.user_id == user_id,
                        func.date(UserAnalytics.date) == today
                    )
                ).first()
                
                if not analytics:
                    analytics = UserAnalytics(user_id=user_id, date=datetime.utcnow())
                    session.add(analytics)
                
                # Соответствие типов статистики полям аналитики
                analytics_mapping = {
                    'total_messages': 'daily_messages',
                    'total_ai_requests': 'daily_ai_requests',
                    'total_games': 'daily_games_played'
                }
                
                if stat_type in analytics_mapping:
                    field = analytics_mapping[stat_type]
                    current_value = getattr(analytics, field) or 0
                    setattr(analytics, field, current_value + increment)
                
                session.commit()
        except Exception as e:
            log_error(f"Ошибка обновления ежедневной аналитики: {str(e)}")

    # Продвинутые методы аналитики
    def get_user_analytics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Получить расширенную аналитику пользователя."""
        with self.get_session() as session:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Получение информации о пользователе
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            # Получение ежедневной аналитики
            daily_analytics = session.query(UserAnalytics).filter(
                and_(
                    UserAnalytics.user_id == user_id,
                    UserAnalytics.date >= start_date
                )
            ).order_by(UserAnalytics.date).all()
            
            # Получение игровых сессий
            game_sessions = session.query(GameSession).filter(
                and_(
                    GameSession.user_id == user_id,
                    GameSession.started_at >= start_date
                )
            ).all()
            
            # Вычисление метрик
            total_messages = sum(d.daily_messages or 0 for d in daily_analytics)
            total_ai_requests = sum(d.daily_ai_requests or 0 for d in daily_analytics)
            total_games = len(game_sessions)
            
            # Производительность в играх
            game_stats = self._calculate_game_performance(game_sessions)
            
            # Паттерны активности
            activity_patterns = self._analyze_activity_patterns(daily_analytics)
            
            return {
                'user_info': user.to_dict(),
                'period_days': days,
                'total_messages': total_messages,
                'total_ai_requests': total_ai_requests,
                'total_games': total_games,
                'game_performance': game_stats,
                'activity_patterns': activity_patterns,
                'daily_analytics': [
                    {
                        'date': d.date.isoformat(),
                        'messages': d.daily_messages or 0,
                        'ai_requests': d.daily_ai_requests or 0,
                        'games': d.daily_games_played or 0,
                        'session_time': d.daily_session_time or 0
                    } for d in daily_analytics
                ]
            }

    def _calculate_game_performance(self, game_sessions: List[GameSession]) -> Dict[str, Any]:
        """Вычисляет производительность в играх."""
        if not game_sessions:
            return {}
        
        game_types = {}
        for session in game_sessions:
            game_type = session.game_type
            if game_type not in game_types:
                game_types[game_type] = {
                    'total': 0,
                    'wins': 0,
                    'avg_score': 0,
                    'avg_duration': 0,
                    'scores': [],
                    'durations': []
                }
            
            stats = game_types[game_type]
            stats['total'] += 1
            
            if session.result == 'win':
                stats['wins'] += 1
            
            if session.score:
                stats['scores'].append(session.score)
            
            if session.duration_seconds:
                stats['durations'].append(session.duration_seconds)
        
        # Вычисление средних значений
        for game_type, stats in game_types.items():
            if stats['scores']:
                stats['avg_score'] = sum(stats['scores']) / len(stats['scores'])
            if stats['durations']:
                stats['avg_duration'] = sum(stats['durations']) / len(stats['durations'])
            stats['win_rate'] = (stats['wins'] / stats['total']) * 100 if stats['total'] > 0 else 0
            
            # Удаление сырых данных
            del stats['scores']
            del stats['durations']
        
        return game_types

    def _analyze_activity_patterns(self, daily_analytics: List[UserAnalytics]) -> Dict[str, Any]:
        """Анализирует паттерны активности."""
        if not daily_analytics:
            return {}
        
        # Самоактивный день
        most_active_day = max(daily_analytics, key=lambda d: d.daily_messages or 0)
        
        # Средняя ежедневная активность
        avg_messages = sum(d.daily_messages or 0 for d in daily_analytics) / len(daily_analytics)
        avg_ai_requests = sum(d.daily_ai_requests or 0 for d in daily_analytics) / len(daily_analytics)
        
        # Тенденция активности (простая линейная тенденция)
        if len(daily_analytics) > 1:
            recent_avg = sum(d.daily_messages or 0 for d in daily_analytics[-7:]) / min(7, len(daily_analytics))
            older_avg = sum(d.daily_messages or 0 for d in daily_analytics[:-7]) / max(1, len(daily_analytics) - 7)
            trend = "увеличивающаяся" if recent_avg > older_avg else "уменьшающаяся" if recent_avg < older_avg else "стабильная"
        else:
            trend = "недостаточно_данных"
        
        return {
            'most_active_date': most_active_day.date.isoformat(),
            'most_active_messages': most_active_day.daily_messages or 0,
            'avg_daily_messages': round(avg_messages, 2),
            'avg_daily_ai_requests': round(avg_ai_requests, 2),
            'activity_trend': trend
        }

    # Улучшенные методы управления игровыми сессиями
    def start_game_session(self, user_id: int, game_type: str, difficulty: str = None, game_data: Dict = None) -> int:
        """Начать улучшенную игровую сессию."""
        with self.get_session() as session:
            game_session = GameSession(
                user_id=user_id,
                game_type=game_type,
                difficulty=difficulty,
                game_data=game_data or {},
                user_choices=[],
                bot_responses=[],
                performance_metrics={}
            )
            session.add(game_session)
            session.commit()
            return game_session.id

    def end_game_session(self, session_id: int, result: str, score: int = 0, attempts: int = 0, **kwargs):
        """Завершить игровую сессию с расширенными метриками."""
        with self.get_session() as session:
            game_session = session.query(GameSession).filter(GameSession.id == session_id).first()
            if game_session:
                game_session.finished_at = datetime.utcnow()
                game_session.result = result
                game_session.score = score
                game_session.attempts = attempts
                
                # Вычисление продолжительности
                if game_session.started_at:
                    duration = datetime.utcnow() - game_session.started_at
                    game_session.duration_seconds = int(duration.total_seconds())
                
                # Добавление метрик производительности
                if kwargs:
                    game_session.performance_metrics = kwargs
                
                session.commit()

    # Улучшенное логирование сообщений
    def log_message(self, user_id: int, message_type: str, content: str = None,
                   response: str = None, processing_time: float = None, **kwargs):
        """Улучшенное логирование сообщений."""
        with self.get_session() as session:
            message_log = MessageLog(
                user_id=user_id,
                message_type=message_type,
                content=content,
                response=response,
                processing_time=processing_time,
                tokens_used=kwargs.get('tokens_used'),
                model_used=kwargs.get('model_used', 'gemini-2.0-flash-exp'),
                success=kwargs.get('success', True),
                error_message=kwargs.get('error_message'),
                context_length=kwargs.get('context_length'),
                message_metadata=kwargs.get('metadata')
            )
            session.add(message_log)
            session.commit()

    # Отслеживание производительности системы
    def log_performance_metrics(self, **metrics):
        """Логирует метрики производительности системы."""
        with self.get_session() as session:
            performance = PerformanceMetrics(
                total_active_users=metrics.get('active_users', 0),
                avg_response_time=metrics.get('avg_response_time', 0.0),
                total_requests_per_hour=metrics.get('requests_per_hour', 0),
                error_rate=metrics.get('error_rate', 0.0),
                ai_model_used=metrics.get('ai_model', 'gemini-2.0-flash-exp'),
                avg_tokens_per_request=metrics.get('avg_tokens', 0.0),
                ai_success_rate=metrics.get('ai_success_rate', 0.0),
                memory_usage_mb=metrics.get('memory_mb'),
                cpu_usage_percent=metrics.get('cpu_percent'),
                metrics_data=metrics.get('additional_data')
            )
            session.add(performance)
            session.commit()

    # Расширенный поиск пользователей с фильтрами
    def search_users_advanced(self, 
                            query: str = None, 
                            min_messages: int = None,
                            max_messages: int = None,
                            created_after: datetime = None,
                            created_before: datetime = None,
                            is_premium: bool = None,
                            favorite_persona: str = None,
                            limit: int = 50) -> List[Dict[str, Any]]:
        """Расширенный поиск пользователей с фильтрами."""
        with self.get_session() as session:
            query_obj = session.query(User)
            
            # Текстовый поиск
            if query:
                query_obj = query_obj.filter(
                    or_(
                        User.id == int(query) if query.isdigit() else False,
                        User.username.ilike(f"%{query}%"),
                        User.first_name.ilike(f"%{query}%"),
                        User.last_name.ilike(f"%{query}%")
                    )
                )
            
            # Числовые фильтры
            if min_messages is not None:
                query_obj = query_obj.filter(User.total_messages >= min_messages)
            if max_messages is not None:
                query_obj = query_obj.filter(User.total_messages <= max_messages)
            
            # Фильтры по дате
            if created_after:
                query_obj = query_obj.filter(User.created_at >= created_after)
            if created_before:
                query_obj = query_obj.filter(User.created_at <= created_before)
            
            # Логические фильтры
            if is_premium is not None:
                query_obj = query_obj.filter(User.is_premium == is_premium)
            
            # Строковые фильтры
            if favorite_persona:
                query_obj = query_obj.filter(User.favorite_persona == favorite_persona)
            
            users = query_obj.order_by(desc(User.last_active)).limit(limit).all()
            return [user.to_dict() for user in users]

    # Расширенная системная статистика
    def get_enhanced_system_stats(self) -> Dict[str, Any]:
        """Получить расширенную системную статистику."""
        with self.get_session() as session:
            # Основные счетчики
            total_users = session.query(func.count(User.id)).scalar()
            active_users_24h = session.query(func.count(User.id)).filter(
                User.last_active >= datetime.utcnow() - timedelta(hours=24)
            ).scalar()
            active_users_7d = session.query(func.count(User.id)).filter(
                User.last_active >= datetime.utcnow() - timedelta(days=7)
            ).scalar()
            
            total_messages = session.query(func.count(MessageLog.id)).scalar()
            total_games = session.query(func.count(GameSession.id)).scalar()
            
            # Статистика типов сообщений
            message_stats = session.query(
                MessageLog.message_type,
                func.count(MessageLog.id)
            ).group_by(MessageLog.message_type).all()
            
            # Статистика типов игр
            game_stats = session.query(
                GameSession.game_type,
                func.count(GameSession.id)
            ).group_by(GameSession.game_type).all()
            
            # Метрики производительности (последние 24 часа)
            recent_performance = session.query(PerformanceMetrics).filter(
                PerformanceMetrics.timestamp >= datetime.utcnow() - timedelta(hours=24)
            ).order_by(desc(PerformanceMetrics.timestamp)).first()
            
            # Метрики вовлеченности пользователей
            avg_messages_per_user = session.query(func.avg(User.total_messages)).scalar() or 0
            avg_games_per_user = session.query(func.avg(User.total_games)).scalar() or 0
            
            # Топ пользователей по активности
            top_users = session.query(User).order_by(desc(User.total_messages)).limit(10).all()
            
            return {
                'users': {
                    'total': total_users or 0,
                    'active_24h': active_users_24h or 0,
                    'active_7d': active_users_7d or 0,
                    'avg_messages_per_user': round(float(avg_messages_per_user), 2),
                    'avg_games_per_user': round(float(avg_games_per_user), 2)
                },
                'activity': {
                    'total_messages': total_messages or 0,
                    'total_games': total_games or 0,
                    'message_types': {stat[0]: stat[1] for stat in message_stats},
                    'game_types': {stat[0]: stat[1] for stat in game_stats}
                },
                'performance': {
                    'avg_response_time': recent_performance.avg_response_time if recent_performance else 0,
                    'error_rate': recent_performance.error_rate if recent_performance else 0,
                    'ai_success_rate': recent_performance.ai_success_rate if recent_performance else 0
                } if recent_performance else {},
                'top_users': [
                    {
                        'id': user.id,
                        'name': user.first_name or 'Неизвестный',
                        'username': user.username,
                        'messages': user.total_messages,
                        'games': user.total_games
                    } for user in top_users
                ]
            }

    # Очистка старых данных для поддержания производительности
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Очищает старые данные для поддержания производительности."""
        with self.get_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Очистка старых логов сообщений
            deleted_messages = session.query(MessageLog).filter(
                MessageLog.created_at < cutoff_date
            ).delete()
            
            # Очистка старых метрик производительности
            deleted_metrics = session.query(PerformanceMetrics).filter(
                PerformanceMetrics.timestamp < cutoff_date
            ).delete()
            
            # Очистка старой аналитики (сохраняем дольше - 1 год)
            analytics_cutoff = datetime.utcnow() - timedelta(days=365)
            deleted_analytics = session.query(UserAnalytics).filter(
                UserAnalytics.date < analytics_cutoff
            ).delete()
            
            session.commit()
            
            log_info(f"Очищено старых данных: {deleted_messages} сообщений, "
                    f"{deleted_metrics} метрик, {deleted_analytics} аналитики")
            
            return {
                'deleted_messages': deleted_messages,
                'deleted_metrics': deleted_metrics,
                'deleted_analytics': deleted_analytics
            }

    # Методы для работы с пользователями

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
                user.total_ai_requests = 0
                user.total_games = 0
                user.total_facts = 0
                user.total_jokes = 0
                user.total_quotes = 0
                user.total_calculations = 0
                user.total_translations = 0
                user.total_weather_requests = 0
                user.total_image_analyses = 0
                user.total_voice_messages = 0
                user.total_documents_processed = 0
                user.total_rps_games = 0
                user.total_quiz_games = 0
                user.total_guess_games = 0
                user.total_dice_games = 0
                user.total_magic_ball_questions = 0
                user.avg_response_time = 0.0
                user.total_session_time = 0
                user.favorite_persona = None
                user.preferred_language = "ru"
                user.user_preferences = None
                user.interaction_patterns = None
                session.commit()

                # Удаляем связанные записи
                session.query(GameSession).filter(GameSession.user_id == user_id).delete()
                session.query(MessageLog).filter(MessageLog.user_id == user_id).delete()
                session.query(UserSettings).filter(UserSettings.user_id == user_id).delete()
                session.query(UserAnalytics).filter(UserAnalytics.user_id == user_id).delete()
                session.commit()

                log_info(f"Статистика пользователя {user_id} очищена")

    def clear_all_users_stats(self):
        """Очистить статистику всех пользователей."""
        with self.get_session() as session:
            # Сбрасываем счетчики пользователей
            session.query(User).update({
                User.total_messages: 0,
                User.total_ai_requests: 0,
                User.total_games: 0,
                User.total_facts: 0,
                User.total_jokes: 0,
                User.total_quotes: 0,
                User.total_calculations: 0,
                User.total_translations: 0,
                User.total_weather_requests: 0,
                User.total_image_analyses: 0,
                User.total_voice_messages: 0,
                User.total_documents_processed: 0,
                User.total_rps_games: 0,
                User.total_quiz_games: 0,
                User.total_guess_games: 0,
                User.total_dice_games: 0,
                User.total_magic_ball_questions: 0,
                User.avg_response_time: 0.0,
                User.total_session_time: 0,
                User.favorite_persona: None,
                User.preferred_language: "ru",
                User.user_preferences: None,
                User.interaction_patterns: None
            })

            # Удаляем все связанные записи
            session.query(GameSession).delete()
            session.query(MessageLog).delete()
            session.query(UserSettings).delete()
            session.query(UserAnalytics).delete()
            session.commit()

            log_info("Статистика всех пользователей очищена")

    def ban_user(self, user_id: int, ban_duration_hours: int = 24):
        """Забанить пользователя."""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.banned_until = datetime.utcnow() + timedelta(hours=ban_duration_hours)
                user.is_banned = True
                session.commit()
                log_info(f"Пользователь {user_id} забанен на {ban_duration_hours} часов")

    def unban_user(self, user_id: int):
        """Разбанить пользователя."""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.banned_until = None
                user.is_banned = False
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
                    user.is_banned = False
                    session.commit()
            return False

    # Методы для работы с играми

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

# Глобальный экземпляр менеджера БД
db_manager = None

def init_database(database_url: str) -> EnhancedDatabaseManager:
    """Инициализировать подключение к улучшенной базе данных."""
    global db_manager
    db_manager = EnhancedDatabaseManager(database_url)
    return db_manager

def get_db_manager() -> EnhancedDatabaseManager:
    """Получить экземпляр улучшенного менеджера БД."""
    return db_manager
