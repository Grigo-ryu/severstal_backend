# Определение модели рулона для работы с базой данных через SQLAlchemy.

from sqlalchemy import Column, Integer, Float, DateTime
from database import Base
from datetime import datetime, UTC


class Roll(Base):
    """Модель рулона с полями: id, длина, вес, дата добавления и удаления."""
    __tablename__ = "rolls"
    
    id = Column(Integer, primary_key=True, index=True)
    length = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    date_added = Column(DateTime, default=lambda: datetime.now(UTC))
    date_removed = Column(DateTime, nullable=True)