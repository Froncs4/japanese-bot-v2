import asyncio
import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base, GrammarPoint, GrammarExample

# Используем SQLite
DB_PATH = os.getenv("DB_PATH", "japanese_bot.db")
DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INITIAL_GRAMMAR = [
    {
        "level": "N5",
        "title": "〜は (wa)",
        "structure": "A wa B desu",
        "description": "Частица は (wa) обозначает тему предложения. Она ставится после слова, которое является темой разговора.",
        "examples": [
            {"japanese": "私は学生です。", "reading": "watashi wa gakusei desu", "translation": "Я студент."},
            {"japanese": "これはペンです。", "reading": "kore wa pen desu", "translation": "Это ручка."}
        ]
    },
    {
        "level": "N5",
        "title": "〜です (desu)",
        "structure": "N + desu",
        "description": "Связка です (desu) используется в конце предложения для вежливости и утверждения (быть, являться).",
        "examples": [
            {"japanese": "いい天気です。", "reading": "ii tenki desu", "translation": "Хорошая погода."},
            {"japanese": "猫です。", "reading": "neko desu", "translation": "Это кошка."}
        ]
    },
    {
        "level": "N5",
        "title": "〜か (ka)",
        "structure": "Sentence + ka",
        "description": "Частица か (ka) в конце предложения превращает его в вопрос.",
        "examples": [
            {"japanese": "学生ですか。", "reading": "gakusei desu ka", "translation": "Вы студент?"},
            {"japanese": "これは何ですか。", "reading": "kore wa nan desu ka", "translation": "Что это?"}
        ]
    }
]

async def seed_grammar():
    engine = create_async_engine(DB_URL, echo=False)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        logger.info("Seeding Grammar N5...")
        
        for g_data in INITIAL_GRAMMAR:
            # Check if exists
            result = await session.execute(
                GrammarPoint.__table__.select().where(GrammarPoint.title == g_data["title"])
            )
            if result.first():
                logger.info(f"Skipping {g_data['title']} (already exists)")
                continue

            point = GrammarPoint(
                level=g_data["level"],
                title=g_data["title"],
                structure=g_data["structure"],
                description=g_data["description"]
            )
            session.add(point)
            await session.flush() # get ID
            
            for ex in g_data["examples"]:
                g_ex = GrammarExample(
                    grammar_id=point.id,
                    japanese=ex["japanese"],
                    reading=ex["reading"],
                    translation=ex["translation"]
                )
                session.add(g_ex)
            
            logger.info(f"Added {g_data['title']}")

        await session.commit()
        logger.info("Seeding completed!")

if __name__ == "__main__":
    asyncio.run(seed_grammar())