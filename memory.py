"""
Модуль для управления памятью и контекстом разговора.
Позволяет боту вести более естественные и осмысленные беседы.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from logger import log_info, log_error


class ConversationMemory:
    """Класс для хранения истории разговора пользователя."""

    def __init__(self, user_id: int, max_messages: int = 20, max_age_hours: int = 24):
        self.user_id = user_id
        self.max_messages = max_messages
        self.max_age_hours = max_age_hours
        self.messages: List[Dict] = []
        self.metadata: Dict = {
            'created_at': datetime.now(),
            'last_updated': datetime.now(),
            'total_messages': 0,
            'current_persona': None,
            'user_preferences': {},
            'game_state': {
                'active_game': None,  # 'guess_number', 'quiz', 'rps', etc.
                'game_data': {},  # additional game data
                'last_game_time': None
            }
        }

    def add_message(self, role: str, content: str, message_type: str = 'text') -> None:
        """Добавить сообщение в историю разговора."""
        message = {
            'role': role,  # 'user' или 'assistant'
            'content': content,
            'timestamp': datetime.now(),
            'type': message_type  # 'text', 'image', 'voice', 'command'
        }

        self.messages.append(message)
        self.metadata['last_updated'] = datetime.now()
        self.metadata['total_messages'] += 1

        # Ограничиваем количество сообщений
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

        log_info(f"Добавлено сообщение в память пользователя {self.user_id}: {role} - {content[:50]}...")

    def get_recent_messages(self, limit: int = 10) -> List[Dict]:
        """Получить последние сообщения из истории."""
        return self.messages[-limit:] if self.messages else []

    def get_context_for_ai(self, limit: int = 8) -> str:
        """Получить контекст для ИИ в удобном формате."""
        recent_messages = self.get_recent_messages(limit)
        if not recent_messages:
            return ""

        context_parts = []
        for msg in recent_messages:
            if msg['type'] == 'command':
                context_parts.append(f"[Команда пользователя: {msg['content']}]")
            elif msg['role'] == 'user':
                context_parts.append(f"Пользователь: {msg['content']}")
            else:
                context_parts.append(f"ИИ: {msg['content'][:200]}...")

        return "\n".join(context_parts[-6:])  # Возвращаем последние 6 сообщений

    def clear_old_messages(self) -> None:
        """Очистить старые сообщения."""
        cutoff_time = datetime.now() - timedelta(hours=self.max_age_hours)
        self.messages = [
            msg for msg in self.messages
            if msg['timestamp'] > cutoff_time
        ]

    def get_statistics(self) -> Dict:
        """Получить статистику разговора."""
        return {
            'total_messages': self.metadata['total_messages'],
            'current_messages': len(self.messages),
            'created_at': self.metadata['created_at'],
            'last_updated': self.metadata['last_updated'],
            'conversation_duration': (self.metadata['last_updated'] - self.metadata['created_at']).total_seconds()
        }

    def set_persona(self, persona_name: str) -> None:
        """Установить текущую персону."""
        self.metadata['current_persona'] = persona_name
        self.metadata['last_updated'] = datetime.now()

    def get_persona(self) -> Optional[str]:
        """Получить текущую персону."""
        return self.metadata.get('current_persona')

    def set_preference(self, key: str, value: any) -> None:
        """Установить пользовательскую настройку."""
        self.metadata['user_preferences'][key] = value
        self.metadata['last_updated'] = datetime.now()

    def get_preference(self, key: str, default: any = None) -> any:
        """Получить пользовательскую настройку."""
        return self.metadata['user_preferences'].get(key, default)

    def set_active_game(self, game_type: str, game_data: Dict = None) -> None:
        """Установить активную игру."""
        # Убедимся, что game_state существует
        if 'game_state' not in self.metadata:
            self.metadata['game_state'] = {
                'active_game': None,
                'game_data': {},
                'last_game_time': None
            }

        self.metadata['game_state']['active_game'] = game_type
        self.metadata['game_state']['game_data'] = game_data or {}
        self.metadata['game_state']['last_game_time'] = datetime.now()
        self.metadata['last_updated'] = datetime.now()

    def get_active_game(self) -> Optional[str]:
        """Получить активную игру."""
        if 'game_state' not in self.metadata:
            return None
        return self.metadata['game_state']['active_game']

    def get_game_data(self) -> Dict:
        """Получить данные активной игры."""
        if 'game_state' not in self.metadata:
            return {}
        return self.metadata['game_state']['game_data']

    def clear_active_game(self) -> None:
        """Очистить активную игру."""
        if 'game_state' in self.metadata:
            self.metadata['game_state']['active_game'] = None
            self.metadata['game_state']['game_data'] = {}
        self.metadata['last_updated'] = datetime.now()

    def is_game_active(self, game_type: str = None) -> bool:
        """Проверить, активна ли игра."""
        active_game = self.get_active_game()
        if game_type:
            return active_game == game_type
        return active_game is not None

    def update_game_data(self, key: str, value: any) -> None:
        """Обновить данные игры."""
        if 'game_state' not in self.metadata:
            self.metadata['game_state'] = {
                'active_game': None,
                'game_data': {},
                'last_game_time': None
            }
        self.metadata['game_state']['game_data'][key] = value
        self.metadata['last_updated'] = datetime.now()


class MemoryManager:
    """Менеджер памяти для всех пользователей."""

    def __init__(self, storage_file: str = 'user_memory.json'):
        self.storage_file = storage_file
        self.memories: Dict[int, ConversationMemory] = {}
        self._load_memories()

    def _load_memories(self) -> None:
        """Загрузить сохраненные воспоминания."""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for user_id_str, memory_data in data.items():
                    user_id = int(user_id_str)
                    memory = ConversationMemory(user_id)
                    memory.messages = memory_data.get('messages', [])
                    memory.metadata = memory_data.get('metadata', memory.metadata)

                    # Преобразуем строки дат обратно в объекты datetime
                    for msg in memory.messages:
                        if 'timestamp' in msg and isinstance(msg['timestamp'], str):
                            msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])

                    # Убедимся, что game_state существует (для совместимости со старыми данными)
                    if 'game_state' not in memory.metadata:
                        memory.metadata['game_state'] = {
                            'active_game': None,
                            'game_data': {},
                            'last_game_time': None
                        }

                    if 'created_at' in memory.metadata and isinstance(memory.metadata['created_at'], str):
                        memory.metadata['created_at'] = datetime.fromisoformat(memory.metadata['created_at'])
                    if 'last_updated' in memory.metadata and isinstance(memory.metadata['last_updated'], str):
                        memory.metadata['last_updated'] = datetime.fromisoformat(memory.metadata['last_updated'])
                    if 'last_game_time' in memory.metadata['game_state'] and isinstance(memory.metadata['game_state']['last_game_time'], str):
                        memory.metadata['game_state']['last_game_time'] = datetime.fromisoformat(memory.metadata['game_state']['last_game_time'])

                    self.memories[user_id] = memory

                log_info(f"Загружены воспоминания для {len(self.memories)} пользователей")
        except Exception as e:
            log_error(f"Ошибка при загрузке воспоминаний: {str(e)}")

    def _save_memories(self) -> None:
        """Сохранить воспоминания на диск."""
        try:
            data = {}
            for user_id, memory in self.memories.items():
                # Убедимся, что game_state существует перед сохранением
                if 'game_state' not in memory.metadata:
                    memory.metadata['game_state'] = {
                        'active_game': None,
                        'game_data': {},
                        'last_game_time': None
                    }

                # Преобразуем datetime в строки для JSON
                memory_data = {
                    'messages': [],
                    'metadata': memory.metadata.copy()
                }

                for msg in memory.messages:
                    msg_copy = msg.copy()
                    if 'timestamp' in msg_copy:
                        msg_copy['timestamp'] = msg_copy['timestamp'].isoformat()
                    memory_data['messages'].append(msg_copy)

                # Преобразуем даты в metadata
                if 'created_at' in memory_data['metadata']:
                    memory_data['metadata']['created_at'] = memory_data['metadata']['created_at'].isoformat()
                if 'last_updated' in memory_data['metadata']:
                    memory_data['metadata']['last_updated'] = memory_data['metadata']['last_updated'].isoformat()

                # Преобразуем даты в game_state
                if 'game_state' in memory_data['metadata'] and memory_data['metadata']['game_state']:
                    game_state = memory_data['metadata']['game_state']
                    if 'last_game_time' in game_state and game_state['last_game_time']:
                        game_state['last_game_time'] = game_state['last_game_time'].isoformat()

                data[str(user_id)] = memory_data

            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            log_error(f"Ошибка при сохранении воспоминаний: {str(e)}")

    def get_memory(self, user_id: int) -> ConversationMemory:
        """Получить или создать память для пользователя."""
        if user_id not in self.memories:
            self.memories[user_id] = ConversationMemory(user_id)
            log_info(f"Создана новая память для пользователя {user_id}")

        return self.memories[user_id]

    def add_user_message(self, user_id: int, content: str, message_type: str = 'text') -> None:
        """Добавить сообщение пользователя."""
        memory = self.get_memory(user_id)
        memory.add_message('user', content, message_type)
        self._save_memories()

    def add_assistant_message(self, user_id: int, content: str, message_type: str = 'text') -> None:
        """Добавить сообщение ассистента."""
        memory = self.get_memory(user_id)
        memory.add_message('assistant', content, message_type)
        self._save_memories()

    def get_user_context(self, user_id: int, limit: int = 8) -> str:
        """Получить контекст разговора для пользователя."""
        memory = self.get_memory(user_id)
        return memory.get_context_for_ai(limit)

    def clear_user_memory(self, user_id: int) -> bool:
        """Очистить память пользователя."""
        if user_id in self.memories:
            del self.memories[user_id]
            self._save_memories()
            log_info(f"Очищена память пользователя {user_id}")
            return True
        return False

    def cleanup_old_memories(self) -> int:
        """Очистить старые воспоминания всех пользователей."""
        cleaned_count = 0
        for memory in self.memories.values():
            old_count = len(memory.messages)
            memory.clear_old_messages()
            if len(memory.messages) < old_count:
                cleaned_count += 1

        if cleaned_count > 0:
            self._save_memories()
            log_info(f"Очищено {cleaned_count} старых воспоминаний")

        return cleaned_count

    def get_user_statistics(self, user_id: int) -> Optional[Dict]:
        """Получить статистику для пользователя."""
        memory = self.get_memory(user_id)
        return memory.get_statistics()

    def update_user_persona(self, user_id: int, persona_name: str) -> None:
        """Обновить персону пользователя."""
        memory = self.get_memory(user_id)
        memory.set_persona(persona_name)
        self._save_memories()

    def get_user_persona(self, user_id: int) -> Optional[str]:
        """Получить персону пользователя."""
        memory = self.get_memory(user_id)
        return memory.get_persona()

    def set_user_preference(self, user_id: int, key: str, value: any) -> None:
        """Установить настройку пользователя."""
        memory = self.get_memory(user_id)
        memory.set_preference(key, value)
        self._save_memories()

    def get_user_preference(self, user_id: int, key: str, default: any = None) -> any:
        """Получить настройку пользователя."""
        memory = self.get_memory(user_id)
        return memory.get_preference(key, default)

    def set_user_active_game(self, user_id: int, game_type: str, game_data: Dict = None) -> None:
        """Установить активную игру для пользователя."""
        memory = self.get_memory(user_id)
        # Убедимся, что game_state инициализирован
        if 'game_state' not in memory.metadata:
            memory.metadata['game_state'] = {
                'active_game': None,
                'game_data': {},
                'last_game_time': None
            }
        memory.set_active_game(game_type, game_data)
        self._save_memories()

    def get_user_active_game(self, user_id: int) -> Optional[str]:
        """Получить активную игру пользователя."""
        memory = self.get_memory(user_id)
        # Убедимся, что game_state инициализирован
        if 'game_state' not in memory.metadata:
            memory.metadata['game_state'] = {
                'active_game': None,
                'game_data': {},
                'last_game_time': None
            }
        return memory.get_active_game()

    def get_user_game_data(self, user_id: int) -> Dict:
        """Получить данные игры пользователя."""
        memory = self.get_memory(user_id)
        # Убедимся, что game_state инициализирован
        if 'game_state' not in memory.metadata:
            memory.metadata['game_state'] = {
                'active_game': None,
                'game_data': {},
                'last_game_time': None
            }
        return memory.get_game_data()

    def clear_user_active_game(self, user_id: int) -> None:
        """Очистить активную игру пользователя."""
        memory = self.get_memory(user_id)
        # Убедимся, что game_state инициализирован
        if 'game_state' not in memory.metadata:
            memory.metadata['game_state'] = {
                'active_game': None,
                'game_data': {},
                'last_game_time': None
            }
        memory.clear_active_game()
        self._save_memories()

    def is_user_game_active(self, user_id: int, game_type: str = None) -> bool:
        """Проверить, активна ли игра у пользователя."""
        memory = self.get_memory(user_id)
        # Убедимся, что game_state инициализирован
        if 'game_state' not in memory.metadata:
            memory.metadata['game_state'] = {
                'active_game': None,
                'game_data': {},
                'last_game_time': None
            }
        return memory.is_game_active(game_type)

    def update_user_game_data(self, user_id: int, key: str, value: any) -> None:
        """Обновить данные игры пользователя."""
        memory = self.get_memory(user_id)
        # Убедимся, что game_state инициализирован
        if 'game_state' not in memory.metadata:
            memory.metadata['game_state'] = {
                'active_game': None,
                'game_data': {},
                'last_game_time': None
            }
        memory.update_game_data(key, value)
        self._save_memories()


# Создаем глобальный экземпляр менеджера памяти
memory_manager = MemoryManager()
