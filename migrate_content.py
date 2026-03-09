import asyncio
import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base, LessonGroup, LessonItem
from data.content import KANJI_N5, KANJI_N5_GROUPS, WORDS_N5, WORDS_N5_GROUPS

# Используем SQLite для начала (совместимо с текущим деплоем)
DB_PATH = os.getenv("DB_PATH", "japanese_bot.db")
DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_content():
    engine = create_async_engine(DB_URL, echo=False)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        # Создаем таблицы, если их нет
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # 1. Migrate KANJI N5
        logger.info("Migrating KANJI N5...")
        for group_key, group_data in KANJI_N5_GROUPS.items():
            # Create Group
            result = await session.execute(
                LessonGroup.__table__.select().where(LessonGroup.key == group_key)
            )
            if not result.first():
                group = LessonGroup(
                    key=group_key,
                    category="kanji_n5",
                    name=group_data["name"],
                    order_index=group_data["order"]
                )
                session.add(group)
            
            # Create Items
            chars = group_data["chars"]
            readings = group_data["readings"]
            hints = group_data["hints"]
            contexts = group_data.get("contexts", [])
            
            for i, char in enumerate(chars):
                # Check if item exists
                # For simplicity, we just add (in real prod, check uniqueness)
                item = LessonItem(
                    group_key=group_key,
                    char=char,
                    reading=readings[i] if i < len(readings) else "",
                    meaning=KANJI_N5.get(char, ""),
                    hint=hints[i] if i < len(hints) else "",
                    context=contexts[i] if i < len(contexts) else "",
                    order_index=i
                )
                session.add(item)
        
        # 2. Migrate WORDS N5
        logger.info("Migrating WORDS N5...")
        for group_key, group_data in WORDS_N5_GROUPS.items():
            result = await session.execute(
                LessonGroup.__table__.select().where(LessonGroup.key == group_key)
            )
            if not result.first():
                group = LessonGroup(
                    key=group_key,
                    category="words_n5",
                    name=group_data["name"],
                    order_index=group_data["order"]
                )
                session.add(group)
            
            chars = group_data["chars"]
            readings = group_data["readings"]
            hints = group_data["hints"]
            contexts = group_data.get("contexts", [])
            
            for i, char in enumerate(chars):
                item = LessonItem(
                    group_key=group_key,
                    char=char,
                    reading=readings[i] if i < len(readings) else "",
                    meaning=WORDS_N5.get(char, ""),
                    hint=hints[i] if i < len(hints) else "",
                    context=contexts[i] if i < len(contexts) else "",
                    order_index=i
                )
                session.add(item)

        await session.commit()
        logger.info("Migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(migrate_content())