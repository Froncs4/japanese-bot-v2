"""
Система планирования задач (уведомления).
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_users_for_reminders
from database import update_leagues_and_reset

async def send_daily_reminders(bot: Bot):
    """Рассылает уведомления пользователям."""
    users = await get_users_for_reminders()
    
    # Кнопка для быстрого перехода к повторению
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 Начать повторение", callback_data="menu:review")]
    ])

    for user_id in users:
        try:
            await bot.send_message(
                chat_id=user_id,
                text="⏰ **Пора повторить японский!**\n\nУ тебя накопились карточки, которые нуждаются в повторении. Зайди на пару минут, чтобы не потерять прогресс и серию!",
                reply_markup=kb
            )
        except Exception as e:
            # Пользователь мог заблокировать бота
            pass

def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """Инициализация планировщика."""
    scheduler = AsyncIOScheduler()
    
    # Ежедневные уведомления в 19:00 по времени сервера
    scheduler.add_job(
        send_daily_reminders,
        trigger="cron",
        hour=19,
        minute=0,
        kwargs={"bot": bot},
    )
    
    # НОВОЕ: Обновление Лиг каждое воскресенье в 23:59
    scheduler.add_job(update_leagues_and_reset, trigger='cron', day_of_week='sun', hour=23, minute=59)
    
    return scheduler
