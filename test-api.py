#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API сервера
"""
import asyncio
import aiohttp
import json

async def test_api():
    base_url = "http://localhost:8080"
    
    async with aiohttp.ClientSession() as session:
        print("🧪 Тестирование API сервера...")
        
        # Тест 1: Проверка доступности сервера
        try:
            async with session.get(f"{base_url}/api/user") as resp:
                print(f"✅ Сервер доступен, статус: {resp.status}")
                if resp.status == 401:
                    print("✅ Требуется авторизация (нормально)")
        except Exception as e:
            print(f"❌ Сервер недоступен: {e}")
            return
        
        # Тест 2: Проверка TTS
        try:
            async with session.get(f"{base_url}/api/tts?text=test") as resp:
                print(f"🔊 TTS статус: {resp.status}")
                if resp.status == 401:
                    print("✅ TTS требует авторизацию (нормально)")
        except Exception as e:
            print(f"❌ TTS ошибка: {e}")
        
        # Тест 3: Проверка leaderboard
        try:
            async with session.get(f"{base_url}/api/leaderboard") as resp:
                print(f"🏆 Leaderboard статус: {resp.status}")
                if resp.status == 401:
                    print("✅ Leaderboard требует авторизацию (нормально)")
        except Exception as e:
            print(f"❌ Leaderboard ошибка: {e}")
        
        print("\n🎯 Если все статусы 401 - сервер работает корректно!")
        print("📝 Для полной работы нужен Telegram WebApp с initData")

if __name__ == "__main__":
    asyncio.run(test_api())
