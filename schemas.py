# Определение Pydantic-схем для валидации запросов и ответов API.

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class RollBase(BaseModel):
    """Базовая схема для рулона с полями длины и веса."""
    length: float
    weight: float


class RollCreate(RollBase):
    """Схема для создания нового рулона (наследуется от RollBase)."""
    pass


class Roll(RollBase):
    """Схема для ответа с данными рулона, включая ID и даты."""
    id: int
    date_added: datetime
    date_removed: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class RollStats(BaseModel):
    """Схема для статистики по рулонам."""
    added_count: int
    removed_count: int
    avg_length: float
    avg_weight: float
    max_length: float
    min_length: float
    max_weight: float
    min_weight: float
    total_weight: float
    max_duration: float
    min_duration: float