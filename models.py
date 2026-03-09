from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, BigInteger
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)  # Telegram User ID
    username = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    xp = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    last_activity = Column(DateTime, default=datetime.utcnow)
    daily_goal = Column(Integer, default=10)
    daily_progress = Column(Integer, default=0)
    daily_date = Column(String, default='')  # YYYY-MM-DD
    coins = Column(Integer, default=0)
    streak_freezes = Column(Integer, default=0)
    league = Column(Integer, default=1)
    weekly_xp = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    progress = relationship("CardProgress", back_populates="user")


class CardProgress(Base):
    __tablename__ = 'card_progress'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    card_type = Column(String, nullable=False)  # kanji_n5, words_n5, etc.
    card_key = Column(String, nullable=False)   # The character or word itself
    ease_factor = Column(Integer, default=250)  # Multiplied by 100 (2.5 -> 250)
    interval_days = Column(Integer, default=0)
    repetitions = Column(Integer, default=0)
    next_review = Column(DateTime, nullable=True)
    last_review = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="progress")


# === CONTENT MODELS ===

class LessonGroup(Base):
    __tablename__ = 'lesson_groups'

    key = Column(String, primary_key=True) # e.g. "n5_numbers"
    category = Column(String, nullable=False) # e.g. "kanji_n5"
    name = Column(String, nullable=False)
    order_index = Column(Integer, default=0)
    
    items = relationship("LessonItem", back_populates="group")


class LessonItem(Base):
    __tablename__ = 'lesson_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_key = Column(String, ForeignKey('lesson_groups.key'), nullable=False)
    char = Column(String, nullable=False) # Kanji or Word
    reading = Column(String, nullable=True)
    meaning = Column(String, nullable=True)
    hint = Column(String, nullable=True)
    context = Column(String, nullable=True)
    order_index = Column(Integer, default=0)

    group = relationship("LessonGroup", back_populates="items")


class GrammarPoint(Base):
    __tablename__ = 'grammar_points'

    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String, nullable=False) # e.g. "N5"
    title = Column(String, nullable=False) # e.g. "〜は〜です (wa...desu)"
    description = Column(Text, nullable=False)
    structure = Column(String, nullable=True) # e.g. "A wa B desu"
    
    examples = relationship("GrammarExample", back_populates="grammar")


class GrammarExample(Base):
    __tablename__ = 'grammar_examples'

    id = Column(Integer, primary_key=True, autoincrement=True)
    grammar_id = Column(Integer, ForeignKey('grammar_points.id'), nullable=False)
    japanese = Column(String, nullable=False)
    reading = Column(String, nullable=True)
    translation = Column(String, nullable=False)
    
    grammar = relationship("GrammarPoint", back_populates="examples")
