import asyncio
import logging
import argparse
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db, get_all_backgrounds
import images
from handlers import get_all_routers
from scheduler import setup_scheduler
from middleware import AntiSpamMiddleware
from api import create_api_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    parser = argparse.ArgumentParser(description="Japanese Learning Bot Service")
    parser.add_argument('--mode', choices=['bot', 'api', 'both'], default='both', help="Service mode to run")
    args = parser.parse_args()

    logger.info(f"Запуск в режиме: {args.mode.upper()}")
    logger.info("Инициализация базы данных...")
    await init_db()
    
    # Проверяем доступность Telegram API
    logger.info("Проверка подключения к Telegram API...")
    try:
        import aiohttp
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get('https://api.telegram.org', timeout=10) as response:
                if response.status == 200:
                    logger.info("✅ Telegram API доступен")
                else:
                    logger.warning(f"⚠️ Telegram API вернул статус: {response.status}")
    except Exception as e:
        logger.error(f"❌ Не удалось подключиться к Telegram API: {e}")
        logger.error("Проверьте подключение к интернету и настройки сети")
        return
    
    saved_bgs = await get_all_backgrounds()
    for screen, bg in saved_bgs.items():
        if screen in images.SCREEN_BACKGROUNDS and bg in images.ASSETS_URLS:
            images.SCREEN_BACKGROUNDS[screen] = bg
    
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не задан в переменных окружения (.env). Бот не может быть запущен.")
        return

    # Инициализация объектов
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.callback_query.middleware(AntiSpamMiddleware(limit_seconds=0.7))
    
    for router in get_all_routers():
        dp.include_router(router)
    logger.info(f"Подключено роутеров: {len(get_all_routers())}")

    api_runner = None

    try:
        # --- ЗАПУСК API ---
        if args.mode in ['api', 'both']:
            api_app = create_api_app()
            api_runner = web.AppRunner(api_app)
            await api_runner.setup()
            api_site = web.TCPSite(api_runner, '0.0.0.0', 8080)
            await api_site.start()
            logger.info("API сервер запущен на порту 8080")

        # --- ЗАПУСК БОТА ---
        if args.mode in ['bot', 'both']:
            scheduler = setup_scheduler(bot)
            scheduler.start()
            
            logger.info("Бот запускается...")
            
            # Попытка запуска поллинга с ретраями
            max_retries = 3
            retry_delay = 5
            for attempt in range(max_retries):
                try:
                    await bot.delete_webhook(drop_pending_updates=True)
                    await dp.start_polling(bot)
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Ошибка подключения ({e}), повтор через {retry_delay}с...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        logger.error("Не удалось подключиться к Telegram API.")
                        raise e

        # Если только API, нужно держать процесс живым
        elif args.mode == 'api':
            logger.info("API Service is running. Press Ctrl+C to stop.")
            # Блокируем выполнение, пока не будет сигнала остановки
            stop_event = asyncio.Event()
            await stop_event.wait()

    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Остановка сервиса...")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        logger.info("Очистка ресурсов...")
        if api_runner:
            await api_runner.cleanup()
        await bot.session.close()
        logger.info("Сервис остановлен.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass