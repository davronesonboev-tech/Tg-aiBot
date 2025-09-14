"""
Клиент для работы с Google Gemini API.
Поддерживает текстовые запросы и мультимодальные запросы с изображениями.
"""

import base64
import json
import requests
from typing import Optional, Dict, Any, List, Union
from io import BytesIO

from config import config
from logger import logger, log_error, log_info
from personas import persona_manager


class GeminiClient:
    """Клиент для взаимодействия с Google Gemini API."""

    def __init__(self):
        """Инициализирует клиент Gemini."""
        self.api_key = config.GOOGLE_API_KEY
        self.model = config.GEMINI_MODEL
        self.timeout = config.REQUEST_TIMEOUT
        self.base_url = config.GEMINI_BASE_URL

    def _prepare_text_request(self, text: str) -> Dict[str, Any]:
        """
        Подготавливает запрос для текстового сообщения.

        Args:
            text: Текстовое сообщение

        Returns:
            Dict с подготовленным запросом
        """
        current_persona = persona_manager.get_current_persona()
        system_message = current_persona.get_system_message()

        # Объединяем системное сообщение с пользовательским текстом
        full_text = f"{system_message}\n\nПользователь: {text}"

        return {
            "contents": [
                {
                    "parts": [
                        {
                            "text": full_text
                        }
                    ]
                }
            ]
        }

    def _prepare_multimodal_request(
        self,
        text: str,
        image_data: bytes,
        mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Подготавливает мультимодальный запрос с изображением.

        Args:
            text: Текстовое сообщение
            image_data: Байты изображения
            mime_type: MIME-тип изображения

        Returns:
            Dict с подготовленным запросом
        """
        current_persona = persona_manager.get_current_persona()
        system_message = current_persona.get_system_message()

        # Объединяем системное сообщение с пользовательским текстом
        full_text = f"{system_message}\n\nПользователь просит проанализировать изображение: {text}"

        # Кодируем изображение в base64
        encoded_image = base64.b64encode(image_data).decode('utf-8')

        return {
            "contents": [
                {
                    "parts": [
                        {
                            "text": full_text
                        },
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": encoded_image
                            }
                        }
                    ]
                }
            ]
        }

    def _make_request(self, payload: Dict[str, Any]) -> Optional[str]:
        """
        Выполняет запрос к Gemini API.

        Args:
            payload: Данные для отправки

        Returns:
            str: Ответ от Gemini или None при ошибке
        """
        try:
            url = config.get_gemini_url(self.model)
            params = {"key": self.api_key}

            headers = {
                "Content-Type": "application/json"
            }

            log_info(f"Отправка запроса к Gemini API: {url}")

            response = requests.post(
                url=url,
                headers=headers,
                params=params,
                json=payload,
                timeout=self.timeout
            )

            response.raise_for_status()

            result = response.json()

            # Извлекаем текст из ответа
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]

            log_error("Не удалось извлечь текст из ответа Gemini API")
            return None

        except requests.exceptions.Timeout:
            log_error("Превышено время ожидания ответа от Gemini API")
            return None
        except requests.exceptions.RequestException as e:
            log_error(f"Ошибка при запросе к Gemini API: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            log_error(f"Ошибка декодирования JSON ответа: {str(e)}")
            return None
        except Exception as e:
            log_error(f"Неожиданная ошибка при работе с Gemini API: {str(e)}")
            return None

    def generate_text_response(self, text: str) -> Optional[str]:
        """
        Генерирует текстовый ответ на основе текстового запроса.

        Args:
            text: Текстовый запрос пользователя

        Returns:
            str: Ответ от Gemini или None при ошибке
        """
        log_info(f"Генерация ответа на текстовый запрос: {text[:100]}...")

        payload = self._prepare_text_request(text)
        response = self._make_request(payload)

        if response:
            log_info("Успешно получен ответ от Gemini API")
        else:
            log_error("Не удалось получить ответ от Gemini API")

        return response

    def analyze_image(self, image_data: bytes, prompt: str = "Опиши это изображение") -> Optional[str]:
        """
        Анализирует изображение с помощью Gemini.

        Args:
            image_data: Байты изображения
            prompt: Промпт для анализа изображения

        Returns:
            str: Описание изображения или None при ошибке
        """
        log_info(f"Анализ изображения, размер: {len(image_data)} байт")

        try:
            payload = self._prepare_multimodal_request(prompt, image_data)
            response = self._make_request(payload)

            if response:
                log_info("Успешно проанализировано изображение")
            else:
                log_error("Не удалось проанализировать изображение")

            return response

        except Exception as e:
            log_error(f"Ошибка при анализе изображения: {str(e)}")
            return None

    def transcribe_audio_with_gemini(self, audio_data: bytes, mime_type: str = "audio/ogg") -> Optional[str]:
        """
        Распознает речь из аудио файла с помощью Gemini API.

        Args:
            audio_data: Байты аудио файла
            mime_type: MIME-тип аудио файла

        Returns:
            str: Распознанный текст или None при ошибке
        """
        log_info(f"Распознавание речи через Gemini, размер: {len(audio_data)} байт")

        try:
            # Кодируем аудио в base64
            encoded_audio = base64.b64encode(audio_data).decode('utf-8')

            current_persona = persona_manager.get_current_persona()
            system_message = current_persona.get_system_message()

            # Специальный промпт для транскрибации
            transcription_prompt = f"{system_message}\n\nЗадача: Распознай текст из этого аудио сообщения. Предоставь ТОЛЬКО транскрибированный текст, без каких-либо дополнительных комментариев или объяснений. Если текст неразборчивый, укажи это кратко."

            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": transcription_prompt
                            },
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": encoded_audio
                                }
                            }
                        ]
                    }
                ]
            }

            response = self._make_request(payload)

            if response:
                log_info("Успешно распознана речь через Gemini")
                return response.strip()
            else:
                log_error("Не удалось распознать речь через Gemini")
                return None

        except Exception as e:
            log_error(f"Ошибка при распознавании речи через Gemini: {str(e)}")
            return None

    def generate_response_with_image(
        self,
        text: str,
        image_data: bytes,
        mime_type: str = "image/jpeg"
    ) -> Optional[str]:
        """
        Генерирует ответ на основе текста и изображения.

        Args:
            text: Текстовый запрос
            image_data: Байты изображения
            mime_type: MIME-тип изображения

        Returns:
            str: Ответ от Gemini или None при ошибке
        """
        log_info(f"Генерация ответа с изображением, текст: {text[:100]}...")

        try:
            payload = self._prepare_multimodal_request(text, image_data, mime_type)
            response = self._make_request(payload)

            if response:
                log_info("Успешно получен ответ с изображением")
            else:
                log_error("Не удалось получить ответ с изображением")

            return response

        except Exception as e:
            log_error(f"Ошибка при генерации ответа с изображением: {str(e)}")
            return None


# Создаем глобальный экземпляр клиента
gemini_client = GeminiClient()
