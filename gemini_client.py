"""
Улучшенный клиент для работы с Google Gemini 2.5 Pro API.
Поддерживает все современные возможности модели: мультимодальность, 
длинный контекст, улучшенное рассуждение, код-генерацию и многое другое.
"""

import base64
import json
import requests
import asyncio
import aiohttp
from typing import Optional, Dict, Any, List, Union, Tuple
from io import BytesIO
from datetime import datetime
import time

from config import config
from logger import logger, log_error, log_info
from personas import persona_manager


class GeminiClient:
    """Улучшенный клиент для взаимодействия с Google Gemini 2.5 Pro API."""

    def __init__(self):
        """Инициализирует клиент Gemini."""
        self.api_key = config.GOOGLE_API_KEY
        self.model = config.GEMINI_MODEL  # Используем модель из конфигурации
        self.timeout = config.REQUEST_TIMEOUT
        self.base_url = config.GEMINI_BASE_URL
        self.session = None
        
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain"
        }
        
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        ]

    async def _get_session(self):
        """Получить или создать aiohttp сессию."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    def _prepare_enhanced_request(
        self, 
        text: str, 
        image_data: bytes = None, 
        audio_data: bytes = None,
        context: str = None,
        task_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Подготавливает улучшенный запрос с поддержкой всех возможностей Gemini 2.5 Pro.
        
        Args:
            text: Текстовое сообщение
            image_data: Байты изображения (опционально)
            audio_data: Байты аудио (опционально)
            context: Контекст разговора
            task_type: Тип задачи для оптимизации промпта
        
        Returns:
            Dict с подготовленным запросом
        """
        current_persona = persona_manager.get_current_persona()
        system_message = current_persona.get_system_message()
        
        enhanced_system = self._get_enhanced_system_prompt(system_message, task_type)
        
        full_prompt = self._build_context_prompt(enhanced_system, text, context)
        
        parts = [{"text": full_prompt}]
        
        if image_data:
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": encoded_image
                }
            })
            
        if audio_data:
            encoded_audio = base64.b64encode(audio_data).decode('utf-8')
            parts.append({
                "inline_data": {
                    "mime_type": "audio/wav",
                    "data": encoded_audio
                }
            })

        return {
            "contents": [{"parts": parts}],
            "generationConfig": self.generation_config,
            "safetySettings": self.safety_settings
        }

    def _get_enhanced_system_prompt(self, base_prompt: str, task_type: str) -> str:
        """Создает улучшенный системный промпт в зависимости от типа задачи."""
        
        task_enhancements = {
            "code": """
Дополнительные инструкции для программирования:
- Всегда объясняй код пошагово
- Предлагай оптимизации и альтернативы
- Указывай потенциальные проблемы
- Добавляй комментарии к сложным частям
- Следуй лучшим практикам языка
""",
            "creative": """
Дополнительные инструкции для творчества:
- Будь максимально креативным и оригинальным
- Используй яркие образы и метафоры
- Предлагай несколько вариантов
- Вдохновляй пользователя
- Думай нестандартно
""",
            "analysis": """
Дополнительные инструкции для анализа:
- Структурируй ответ логически
- Приводи конкретные примеры
- Рассматривай разные точки зрения
- Делай обоснованные выводы
- Указывай источники если возможно
""",
            "math": """
Дополнительные инструкции для математики:
- Показывай пошаговое решение
- Объясняй каждый шаг
- Проверяй результат
- Предлагай альтернативные методы
- Визуализируй если нужно
""",
            "translation": """
Дополнительные инструкции для перевода:
- Сохраняй смысл и тон оригинала
- Адаптируй культурные особенности
- Объясняй сложные моменты
- Предлагай альтернативные варианты
- Учитывай контекст
"""
        }
        
        enhancement = task_enhancements.get(task_type, "")
        return f"{base_prompt}\n\n{enhancement}".strip()

    def _build_context_prompt(self, system_message: str, text: str, context: str = None) -> str:
        """Строит промпт с учетом контекста."""
        
        prompt_parts = [system_message]
        
        if context:
            prompt_parts.append(f"\nКонтекст предыдущего разговора:\n{context}")
            
        prompt_parts.append(f"\nТекущий запрос пользователя: {text}")
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        prompt_parts.append(f"\nТекущее время: {current_time}")
        
        return "\n".join(prompt_parts)

    async def _make_async_request(self, payload: Dict[str, Any]) -> Optional[str]:
        """Выполняет асинхронный запрос к Gemini API."""
        try:
            url = config.get_gemini_url(self.model)
            params = {"key": self.api_key}
            headers = {"Content-Type": "application/json"}
            
            session = await self._get_session()
            
            log_info(f"Отправка запроса к Gemini 2.5 Pro: {url}")
            
            async with session.post(
                url=url,
                headers=headers,
                params=params,
                json=payload
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                return self._extract_response_text(result)
                
        except asyncio.TimeoutError:
            log_error("Превышено время ожидания ответа от Gemini API")
            return None
        except aiohttp.ClientError as e:
            log_error(f"Ошибка при запросе к Gemini API: {str(e)}")
            return None
        except Exception as e:
            log_error(f"Неожиданная ошибка при работе с Gemini API: {str(e)}")
            return None

    def _extract_response_text(self, result: Dict[str, Any]) -> Optional[str]:
        """Извлекает текст из ответа API с улучшенной обработкой."""
        try:
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                
                finish_reason = candidate.get("finishReason", "")
                if finish_reason == "SAFETY":
                    return "❌ Извините, не могу ответить на этот запрос по соображениям безопасности."
                elif finish_reason == "MAX_TOKENS":
                    log_info("Ответ был обрезан из-за лимита токенов")
                
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]
                        
            log_error("Не удалось извлечь текст из ответа Gemini API")
            return None
            
        except Exception as e:
            log_error(f"Ошибка при извлечении текста из ответа: {str(e)}")
            return None

    async def generate_text_response_async(
        self, 
        text: str, 
        context: str = None, 
        task_type: str = "general"
    ) -> Optional[str]:
        """Асинхронно генерирует текстовый ответ."""
        log_info(f"Генерация ответа на текстовый запрос: {text[:100]}...")
        
        payload = self._prepare_enhanced_request(text, context=context, task_type=task_type)
        response = await self._make_async_request(payload)
        
        if response:
            log_info("Успешно получен ответ от Gemini 2.5 Pro")
        else:
            log_error("Не удалось получить ответ от Gemini 2.5 Pro")
            
        return response

    async def analyze_image_async(
        self, 
        image_data: bytes, 
        prompt: str = "Детально опиши это изображение",
        context: str = None
    ) -> Optional[str]:
        """Асинхронно анализирует изображение."""
        log_info(f"Анализ изображения, размер: {len(image_data)} байт")
        
        try:
            payload = self._prepare_enhanced_request(
                prompt, 
                image_data=image_data, 
                context=context,
                task_type="analysis"
            )
            response = await self._make_async_request(payload)
            
            if response:
                log_info("Успешно проанализировано изображение")
            else:
                log_error("Не удалось проанализировать изображение")
                
            return response
            
        except Exception as e:
            log_error(f"Ошибка при анализе изображения: {str(e)}")
            return None

    async def transcribe_audio_async(
        self, 
        audio_data: bytes, 
        mime_type: str = "audio/ogg"
    ) -> Optional[str]:
        """Асинхронно распознает речь из аудио."""
        log_info(f"Распознавание речи через Gemini 2.5 Pro, размер: {len(audio_data)} байт")
        
        try:
            prompt = """Задача: Распознай текст из этого аудио сообщения. 
            Предоставь ТОЛЬКО транскрибированный текст на том же языке, что и в аудио.
            Если текст неразборчивый, укажи это кратко."""
            
            payload = self._prepare_enhanced_request(
                prompt,
                audio_data=audio_data,
                task_type="transcription"
            )
            response = await self._make_async_request(payload)
            
            if response:
                log_info("Успешно распознана речь через Gemini 2.5 Pro")
                return response.strip()
            else:
                log_error("Не удалось распознать речь через Gemini 2.5 Pro")
                return None
                
        except Exception as e:
            log_error(f"Ошибка при распознавании речи: {str(e)}")
            return None

    def detect_task_type(self, text: str) -> str:
        """Определяет тип задачи для оптимизации промпта."""
        text_lower = text.lower()
        
        # Математика и вычисления
        if any(op in text for op in ['+', '-', '*', '/', '=', '²', '³']) or \
           any(word in text_lower for word in ['вычисли', 'посчитай', 'реши', 'математика', 'формула']):
            return "math"
            
        # Программирование
        if any(word in text_lower for word in ['код', 'программа', 'функция', 'алгоритм', 'python', 'javascript', 'html', 'css']):
            return "code"
            
        # Перевод
        if any(word in text_lower for word in ['переведи', 'translate', 'перевод', 'на английский', 'на русский']):
            return "translation"
            
        # Творчество
        if any(word in text_lower for word in ['придумай', 'создай', 'напиши стих', 'история', 'сказка', 'креатив']):
            return "creative"
            
        # Анализ
        if any(word in text_lower for word in ['анализ', 'сравни', 'объясни', 'разбери', 'почему', 'как работает']):
            return "analysis"
            
        return "general"

    def generate_text_response(self, text: str, context: str = None) -> Optional[str]:
        """Синхронная обертка для генерации текста."""
        task_type = self.detect_task_type(text)
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(
                self.generate_text_response_async(text, context, task_type)
            )
        except RuntimeError:
            # Если цикл событий уже запущен, создаем новый
            import threading
            result = [None]
            
            def run_async():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result[0] = new_loop.run_until_complete(
                        self.generate_text_response_async(text, context, task_type)
                    )
                finally:
                    new_loop.close()
            
            thread = threading.Thread(target=run_async)
            thread.start()
            thread.join()
            return result[0]

    def analyze_image(self, image_data: bytes, prompt: str = "Детально опиши это изображение") -> Optional[str]:
        """Синхронная обертка для анализа изображений."""
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(
                self.analyze_image_async(image_data, prompt)
            )
        except RuntimeError:
            import threading
            result = [None]
            
            def run_async():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result[0] = new_loop.run_until_complete(
                        self.analyze_image_async(image_data, prompt)
                    )
                finally:
                    new_loop.close()
            
            thread = threading.Thread(target=run_async)
            thread.start()
            thread.join()
            return result[0]

    def transcribe_audio_with_gemini(self, audio_data: bytes, mime_type: str = "audio/ogg") -> Optional[str]:
        """Синхронная обертка для распознавания речи."""
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(
                self.transcribe_audio_async(audio_data, mime_type)
            )
        except RuntimeError:
            import threading
            result = [None]
            
            def run_async():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result[0] = new_loop.run_until_complete(
                        self.transcribe_audio_async(audio_data, mime_type)
                    )
                finally:
                    new_loop.close()
            
            thread = threading.Thread(target=run_async)
            thread.start()
            thread.join()
            return result[0]

    async def generate_with_tools_async(self, text: str, available_tools: List[str]) -> Tuple[Optional[str], Optional[str]]:
        """Генерирует ответ с возможностью использования инструментов."""
        tools_prompt = f"""
У тебя есть доступ к следующим инструментам: {', '.join(available_tools)}

Если пользователь просит что-то, что можно сделать с помощью этих инструментов, 
сначала укажи какой инструмент нужно использовать в формате: TOOL: название_инструмента

Запрос пользователя: {text}
"""
        
        response = await self.generate_text_response_async(tools_prompt, task_type="analysis")
        
        if response and response.startswith("TOOL:"):
            lines = response.split('\n', 1)
            tool_name = lines[0].replace("TOOL:", "").strip()
            explanation = lines[1] if len(lines) > 1 else ""
            return explanation, tool_name
            
        return response, None

    async def close(self):
        """Закрывает сессию."""
        if self.session and not self.session.closed:
            await self.session.close()


# Создаем глобальный экземпляр клиента
gemini_client = GeminiClient()
