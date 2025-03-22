# Настройка базы данных SQLite и создание сессий для работы с ней.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


# Устанавливаем URL базы данных (по умолчанию SQLite с файлом rolls.db)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///rolls.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей SQLAlchemy
Base = declarative_base()


def get_db():
    """
    Генератор для создания сессии базы данных.
    Используется как зависимость в FastAPI для управления сессиями.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()