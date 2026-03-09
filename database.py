"""
База данных с ежедневными целями, статистикой, блиц-рекордами,
настройками фонов и ачивками.
"""

import aiosqlite
from datetime import datetime, date, timedelta
from config import DB_PATH, QUIZ_COOLDOWN, MAX_DAILY_QUIZZES

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT DEFAULT '',
                photo_url TEXT DEFAULT '',
                xp INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 0,
                best_streak INTEGER DEFAULT 0,
                last_activity TEXT DEFAULT '',
                daily_goal INTEGER DEFAULT 10,
                daily_progress INTEGER DEFAULT 0,
                daily_date TEXT DEFAULT '',
                total_reviews INTEGER DEFAULT 0,
                correct_reviews INTEGER DEFAULT 0,
                created_at TEXT DEFAULT '',
                best_blitz_score INTEGER DEFAULT 0,
                weekly_progress INTEGER DEFAULT 0,
                weekly_date TEXT DEFAULT '',
                voice_msgs INTEGER DEFAULT 0,
                night_owl INTEGER DEFAULT 0,
                grammar_perfect INTEGER DEFAULT 0,
                wheel_date TEXT DEFAULT '',
                last_quiz_time TEXT DEFAULT '',
                daily_quiz_count INTEGER DEFAULT 0,
                last_quiz_date TEXT DEFAULT ''
            )
        """)
        
        # Безопасное добавление новых колонок (для старых версий БД)
        new_columns = [
            "coins INTEGER DEFAULT 0",             # Монеты
            "streak_freezes INTEGER DEFAULT 0",    # Заморозка серии
            "league INTEGER DEFAULT 1",            # Лига (1-Бронза, 5-Легенда)
            "weekly_xp INTEGER DEFAULT 0"          # Опыт за неделю
        ]
        for col in new_columns:
            try:
                await db.execute(f"ALTER TABLE users ADD COLUMN {col}")
            except Exception:
                pass

        await db.execute("""
            CREATE TABLE IF NOT EXISTS card_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                card_type TEXT NOT NULL,
                card_key TEXT NOT NULL,
                ease_factor REAL DEFAULT 2.5,
                interval_days REAL DEFAULT 0,
                repetitions INTEGER DEFAULT 0,
                next_review TEXT DEFAULT '',
                last_review TEXT DEFAULT '',
                UNIQUE(user_id, card_type, card_key)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS media_cache (
                media_key TEXT PRIMARY KEY,
                file_id TEXT NOT NULL,
                media_type TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL
            )
        """)
        await db.commit()


# ==========================================================
# ПОЛЬЗОВАТЕЛИ И ПРОГРЕСС
# ==========================================================
async def get_or_create_user(user_id: int, username: str = "", photo_url: str = "") -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()

        today = date.today().isoformat()
        now = datetime.now().isoformat()
        current_week = datetime.now().strftime("%Y-%W")

        if row:
            user = dict(row)
            
            # 🔥 ИСПРАВЛЕНИЕ: Блокируем перезапись имени, если оно уже задано через /setname
            if username and username not in ["User", "Test User", "Пользователь"]:
                # Обновляем имя в БД только если там пусто или стоит стандартное
                if not user.get("username") or user.get("username") in ["User", "Ученик", "Test User"]:
                    await db.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
                    user["username"] = username
            
            if photo_url and user.get("photo_url") != photo_url:
                await db.execute("UPDATE users SET photo_url = ? WHERE user_id = ?", (photo_url, user_id))
                user["photo_url"] = photo_url

            if user.get("daily_date") != today:
                await db.execute("UPDATE users SET daily_progress = 0, daily_date = ? WHERE user_id = ?", (today, user_id))
                user["daily_progress"] = 0
                user["daily_date"] = today
            if user.get("last_quiz_date") != today:
                await db.execute("UPDATE users SET daily_quiz_count = 0, last_quiz_date = ? WHERE user_id = ?", (today, user_id))
            
            await db.commit()
            return user

        actual_username = username if username and username not in ["User", "Test User", "Пользователь"] else f"Ученик {user_id}"
        await db.execute(
            """INSERT INTO users (
                user_id, username, photo_url, xp, current_streak, best_streak,
                last_activity, daily_goal, daily_progress, daily_date, total_reviews,
                correct_reviews, created_at, best_blitz_score, weekly_progress, weekly_date,
                last_quiz_time, daily_quiz_count, last_quiz_date,
                coins, streak_freezes, league, weekly_xp
               ) VALUES (?, ?, ?, 0, 0, 0, ?, 10, 0, ?, 0, 0, ?, 0, 0, ?, '', 0, ?, 0, 0, 1, 0)""",
            (user_id, actual_username, photo_url, current_week, today, now, current_week, today)
        )
        await db.commit()
        return await get_or_create_user(user_id, actual_username, photo_url)


# 🔥 ИСПРАВЛЕНИЕ: Восстановлен реальный SQL-запрос для сбора статистики карточек
async def get_user_stats(user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = await cursor.fetchone()
        if not user: return {}

        # Группируем изученные карточки
        cursor = await db.execute("SELECT card_type, COUNT(*) as cnt FROM card_progress WHERE user_id = ? AND repetitions > 0 GROUP BY card_type", (user_id,))
        rows = await cursor.fetchall()
        cards_by_type = {row['card_type']: row['cnt'] for row in rows}
        total_learned = sum(cards_by_type.values())

        accuracy = 0
        if user['total_reviews'] > 0:
            accuracy = user['correct_reviews'] / user['total_reviews']

        return {
            "xp": user["xp"],
            "current_streak": user["current_streak"],
            "best_streak": user["best_streak"],
            "total_learned": total_learned,
            "accuracy": accuracy,
            "cards_by_type": cards_by_type,
            "best_blitz_score": user["best_blitz_score"],
            "voice_msgs": user["voice_msgs"]
        }


async def add_xp(user_id: int, amount: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        # Даем 1 монету за каждые 5 XP
        coins_earned = amount // 5
        await db.execute("UPDATE users SET xp = xp + ?, weekly_xp = weekly_xp + ?, coins = coins + ? WHERE user_id = ?", 
                         (amount, amount, coins_earned, user_id))
        await db.commit()
        cursor = await db.execute("SELECT xp FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else 0


async def update_streak(user_id: int, correct: bool) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT current_streak, best_streak, last_activity, streak_freezes FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if not row: return {"current_streak": 0, "best_streak": 0}

        today = date.today().isoformat()
        last_act = row["last_activity"][:10] if row["last_activity"] else ""
        current = row["current_streak"]
        best = row["best_streak"]
        freezes = row["streak_freezes"]

        if last_act != today:
            yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
            if last_act == yesterday or current == 0:
                current += 1
            else:
                # СПАСАЕМ СЕРИЮ, ЕСЛИ ЕСТЬ ЗАМОРОЗКА!
                if freezes > 0:
                    await db.execute("UPDATE users SET streak_freezes = streak_freezes - 1 WHERE user_id = ?", (user_id,))
                    current += 1
                else:
                    current = 1

        if current > best: best = current

        await db.execute("UPDATE users SET current_streak = ?, best_streak = ?, last_activity = ? WHERE user_id = ?", 
                         (current, best, datetime.now().isoformat(), user_id))
        if correct: await db.execute("UPDATE users SET correct_reviews = correct_reviews + 1, total_reviews = total_reviews + 1 WHERE user_id = ?", (user_id,))

        await db.commit()
        return {"current_streak": current, "best_streak": best}


async def claim_wheel_reward(user_id: int, reward: int) -> bool:
    today = date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT wheel_date FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if row and row[0] == today:
            return False
        await db.execute("UPDATE users SET xp = xp + ?, wheel_date = ? WHERE user_id = ?", (reward, today, user_id))
        await db.commit()
        return True


async def add_daily_progress(user_id: int, amount: int = 1) -> tuple:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT daily_progress, daily_goal, weekly_progress FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if not row: return 0, 10, False, False
        prog, goal, wp = row[0], row[1], row[2]
        
        new_prog = prog + amount
        new_wp = wp + amount
        just_done_daily = (prog < goal and new_prog >= goal)
        just_done_weekly = (wp < goal*7 and new_wp >= goal*7)

        await db.execute("UPDATE users SET daily_progress = ?, weekly_progress = ? WHERE user_id = ?", (new_prog, new_wp, user_id))
        await db.commit()
        return new_prog, goal, just_done_daily, just_done_weekly


async def update_blitz_score(user_id: int, score: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT best_blitz_score FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if row and score > row[0]:
            await db.execute("UPDATE users SET best_blitz_score = ? WHERE user_id = ?", (score, user_id))
            await db.commit()
            return True
        return False


async def update_stats_and_achievements(user_id: int, xp_amount: int = 0, is_grammar_perfect: bool = False, is_voice: bool = False, is_night: bool = False):
    async with aiosqlite.connect(DB_PATH) as db:
        if is_grammar_perfect: await db.execute("UPDATE users SET grammar_perfect = grammar_perfect + 1 WHERE user_id = ?", (user_id,))
        if is_voice: await db.execute("UPDATE users SET voice_msgs = voice_msgs + 1 WHERE user_id = ?", (user_id,))
        if is_night: await db.execute("UPDATE users SET night_owl = 1 WHERE user_id = ?", (user_id,))
        if xp_amount > 0: await db.execute("UPDATE users SET xp = xp + ? WHERE user_id = ?", (xp_amount, user_id))
        await db.commit()


async def get_all_backgrounds() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT setting_key, setting_value FROM settings WHERE setting_key LIKE 'bg_%'")
        return {row[0].replace('bg_', ''): row[1] for row in await cursor.fetchall()}

async def set_background(screen: str, bg_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?)", (f"bg_{screen}", bg_name))
        await db.commit()

async def get_cached_media(media_key: str) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT file_id FROM media_cache WHERE media_key = ?", (media_key,))
        row = await cursor.fetchone()
        return row[0] if row else None

async def set_cached_media(media_key: str, file_id: str, media_type: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO media_cache (media_key, file_id, media_type, created_at) VALUES (?, ?, ?, ?)", 
                         (media_key, file_id, media_type, datetime.now().isoformat()))
        await db.commit()

async def get_weakest_cards(user_id: int, card_type: str, limit: int = 5) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT card_key FROM card_progress WHERE user_id = ? AND card_type = ? ORDER BY ease_factor ASC, interval_days ASC LIMIT ?", (user_id, card_type, limit))
        return [row[0] for row in await cursor.fetchall()]

async def get_card_progress(user_id: int, card_type: str, card_key: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM card_progress WHERE user_id = ? AND card_type = ? AND card_key = ?", (user_id, card_type, card_key))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def upsert_card_progress(user_id: int, card_type: str, card_key: str, ease_factor: float, interval_days: float, repetitions: int, next_review: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO card_progress (user_id, card_type, card_key, ease_factor, interval_days, repetitions, next_review, last_review)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, card_type, card_key) DO UPDATE SET
            ease_factor=excluded.ease_factor, interval_days=excluded.interval_days, 
            repetitions=excluded.repetitions, next_review=excluded.next_review, last_review=excluded.last_review
        """, (user_id, card_type, card_key, ease_factor, interval_days, repetitions, next_review, datetime.now().isoformat()))
        await db.commit()

async def check_quiz_cooldown(user_id: int) -> tuple[bool, int]:
    """
    Проверяет, можно ли сейчас запускать новый квиз.
    Возвращает (allowed, remaining_seconds).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT last_quiz_time, daily_quiz_count, last_quiz_date FROM users WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return True, 0

        today = date.today().isoformat()
        last_quiz_date = row["last_quiz_date"] or ""
        daily_quiz_count = row["daily_quiz_count"] or 0

        # Новый день — обнуляем счётчик
        if last_quiz_date != today:
            await db.execute(
                "UPDATE users SET daily_quiz_count = 0, last_quiz_date = ? WHERE user_id = ?",
                (today, user_id),
            )
            await db.commit()
            return True, 0

        # Проверка дневного лимита
        if daily_quiz_count >= MAX_DAILY_QUIZZES:
            return False, 0

        last_quiz_time = row["last_quiz_time"] or ""
        if not last_quiz_time:
            return True, 0

        try:
            last_dt = datetime.fromisoformat(last_quiz_time)
        except Exception:
            return True, 0

        elapsed = (datetime.now() - last_dt).total_seconds()
        if elapsed >= QUIZ_COOLDOWN:
            return True, 0

        remaining = int(QUIZ_COOLDOWN - elapsed)
        return False, max(0, remaining)

async def update_quiz_attempt(user_id: int):
    """Фиксирует попытку прохождения квиза (для кулдауна и дневного лимита)."""
    now = datetime.now().isoformat()
    today = date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT daily_quiz_count, last_quiz_date FROM users WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
        if row:
            daily_quiz_count = row[0] or 0
            last_quiz_date = row[1] or ""
            if last_quiz_date != today:
                daily_quiz_count = 0
        else:
            daily_quiz_count = 0

        await db.execute(
            """
            UPDATE users
            SET last_quiz_time = ?, last_quiz_date = ?, daily_quiz_count = ?
            WHERE user_id = ?
            """,
            (now, today, daily_quiz_count + 1, user_id),
        )
        await db.commit()

async def get_users_for_reminders() -> list[int]:
    """
    Возвращает список пользователей, у которых есть карточки для повторения.
    Используется планировщиком для ежедневных напоминаний.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        now = datetime.now().isoformat()
        cursor = await db.execute(
            """
            SELECT DISTINCT user_id
            FROM card_progress
            WHERE next_review != '' AND next_review <= ?
            """,
            (now,),
        )
        rows = await cursor.fetchall()
        return [row["user_id"] for row in rows]

async def get_top_players(limit: int = 10) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT user_id, username, photo_url, xp, current_streak, league FROM users ORDER BY xp DESC LIMIT ?", (limit,))
        return [dict(row) for row in await cursor.fetchall()]

async def get_top_blitz(limit: int = 10) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT user_id, username, photo_url, xp, best_blitz_score, current_streak FROM users ORDER BY best_blitz_score DESC LIMIT ?", (limit,))
        return [dict(row) for row in await cursor.fetchall()]

async def get_due_reviews(user_id: int, limit: int = 15) -> list[dict]:
    """Возвращает карточки, которые пора повторить."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        now = datetime.now().isoformat()
        cursor = await db.execute(
            "SELECT card_type, card_key FROM card_progress WHERE user_id = ? AND next_review <= ? ORDER BY next_review ASC LIMIT ?",
            (user_id, now, limit)
        )
        return [dict(row) for row in await cursor.fetchall()]

async def buy_shop_item(user_id: int, item_id: str, price: int) -> bool:
    """Покупка предметов в магазине."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if not row or row[0] < price: return False  # Не хватает денег
        
        if item_id == "freeze":
            await db.execute("UPDATE users SET coins = coins - ?, streak_freezes = streak_freezes + 1 WHERE user_id = ?", (price, user_id))
        else:
            return False # Пока только заморозка
            
        await db.commit()
        return True

async def update_leagues_and_reset():
    """Еженедельный сброс Лиг: Топ-20% идут вверх, нижние 20% падают."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT user_id, league, weekly_xp FROM users WHERE weekly_xp > 0 ORDER BY league DESC, weekly_xp DESC")
        players = await cursor.fetchall()

        leagues = {1:[], 2:[], 3:[], 4:[], 5:[]}
        for p in players: leagues[p['league']].append(p)

        for l_id, members in leagues.items():
            if not members: continue
            promote_count = max(1, int(len(members) * 0.2))
            demote_count = max(1, int(len(members) * 0.2))

            for i, m in enumerate(members):
                new_l = m['league']
                if i < promote_count and new_l < 5: new_l += 1
                elif i >= len(members) - demote_count and new_l > 1: new_l -= 1
                await db.execute("UPDATE users SET league = ?, weekly_xp = 0 WHERE user_id = ?", (new_l, m['user_id']))
        await db.commit()
