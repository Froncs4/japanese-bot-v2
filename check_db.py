import asyncio
import os
import aiosqlite

DB_PATH = os.getenv("DB_PATH", "japanese_bot.db")

async def check_data():
    print(f"Checking DB at {DB_PATH}...")
    async with aiosqlite.connect(DB_PATH) as db:
        # Check users table schema
        cursor = await db.execute("PRAGMA table_info(users)")
        columns = await cursor.fetchall()
        print("Users table columns:")
        for col in columns:
            print(f" - {col[1]} ({col[2]})")
            
        # Check user count
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        count = await cursor.fetchone()
        print(f"\nTotal users: {count[0]}")

        # Check card_progress
        cursor = await db.execute("SELECT COUNT(*) FROM card_progress")
        count = await cursor.fetchone()
        print(f"Total card progress records: {count[0]}")

if __name__ == "__main__":
    asyncio.run(check_data())