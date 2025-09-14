#!/usr/bin/env python3
"""Тестовый скрипт для проверки utils.py"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import game_service

def test_game_service():
    """Тестирование GameService."""
    print("🧪 Тестирование GameService...")

    # Тестируем базовый метод
    try:
        result = game_service.test_method()
        print(f"✅ test_method: {result}")
    except Exception as e:
        print(f"❌ test_method failed: {e}")

    # Тестируем play_dice_game
    try:
        result = game_service.play_dice_game('medium')
        print(f"✅ play_dice_game: {result[:50]}...")
    except Exception as e:
        print(f"❌ play_dice_game failed: {e}")

    # Проверяем атрибуты объекта
    print(f"📋 Атрибуты game_service: {dir(game_service)}")
    print(f"🎲 Есть play_dice_game: {hasattr(game_service, 'play_dice_game')}")
    print(f"🎲 Тип play_dice_game: {type(getattr(game_service, 'play_dice_game', None))}")

if __name__ == "__main__":
    test_game_service()
