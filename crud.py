# Этот файл содержит функции для работы с базой данных (CRUD операции: создание, удаление, получение и статистика рулонов).

from sqlalchemy.orm import Session
from models import Roll
from schemas import RollCreate
from datetime import datetime, UTC
from sqlalchemy.sql import func


def create_roll(db: Session, roll: RollCreate):
    """Создаёт новый рулон в базе данных."""
    db_roll = Roll(length=roll.length, weight=roll.weight)
    db.add(db_roll)
    db.commit()
    db.refresh(db_roll)
    return db_roll


def delete_roll(db: Session, roll_id: int):
    """
    Выполняет мягкое удаление рулона (устанавливает date_removed).
    Возвращает рулон, если он найден и не был удалён ранее, иначе None.
    """
    roll = db.query(Roll).filter(Roll.id == roll_id, Roll.date_removed.is_(None)).first()
    if roll:
        roll.date_removed = datetime.now(UTC)
        db.commit()
        db.refresh(roll)
    return roll


def get_rolls(db: Session, **filters):
    """
    Получает список рулонов с применением фильтров (по id, весу, длине, датам).
    Фильтры передаются как именованные аргументы (например, id_range, weight_range).
    """
    query = db.query(Roll)
    
    if 'id_range' in filters:
        id_min, id_max = filters['id_range']
        query = query.filter(Roll.id.between(id_min, id_max))
    
    if 'weight_range' in filters:
        weight_min, weight_max = filters['weight_range']
        query = query.filter(Roll.weight.between(weight_min, weight_max))
    
    if 'length_range' in filters:
        length_min, length_max = filters['length_range']
        query = query.filter(Roll.length.between(length_min, length_max))
    
    if 'date_added_range' in filters:
        date_added_min, date_added_max = filters['date_added_range']
        query = query.filter(Roll.date_added.between(date_added_min, date_added_max))
    
    if 'date_removed_range' in filters:
        date_removed_min, date_removed_max = filters['date_removed_range']
        query = query.filter(Roll.date_removed.between(date_removed_min, date_removed_max))
    
    return query.all()


def get_roll_stats(db: Session, start_date: datetime, end_date: datetime):
    """
    Вычисляет статистику по рулонам за заданный период (start_date, end_date).
    Возвращает словарь с количеством добавленных/удалённых рулонов, средними значениями и т.д.
    """
    rolls = db.query(Roll).filter(Roll.date_added.between(start_date, end_date))
    
    added_count = rolls.count()
    removed_count = rolls.filter(Roll.date_removed.isnot(None)).count()
    
    stats = rolls.with_entities(
        func.avg(Roll.length).label('avg_length'),
        func.avg(Roll.weight).label('avg_weight'),
        func.max(Roll.length).label('max_length'),
        func.min(Roll.length).label('min_length'),
        func.max(Roll.weight).label('max_weight'),
        func.min(Roll.weight).label('min_weight'),
        func.sum(Roll.weight).label('total_weight'),
        func.max(func.julianday(Roll.date_removed) - func.julianday(Roll.date_added)).label('max_duration'),
        func.min(func.julianday(Roll.date_removed) - func.julianday(Roll.date_added)).label('min_duration')
    ).first()
    
    return {
        "added_count": added_count,
        "removed_count": removed_count,
        "avg_length": stats.avg_length or 0,
        "avg_weight": stats.avg_weight or 0,
        "max_length": stats.max_length or 0,
        "min_length": stats.min_length or 0,
        "max_weight": stats.max_weight or 0,
        "min_weight": stats.min_weight or 0,
        "total_weight": stats.total_weight or 0,
        "max_duration": stats.max_duration or 0,
        "min_duration": stats.min_duration or 0
    }