# Основной файл приложения FastAPI с определением маршрутов API.

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from database import get_db, Base, engine
from schemas import RollCreate, Roll, RollStats
from crud import create_roll, delete_roll, get_rolls, get_roll_stats


app = FastAPI(debug=True)

# Создаём таблицы в базе данных при запуске приложения
Base.metadata.create_all(bind=engine)


@app.post("/rolls/", response_model=Roll)
def create_new_roll(roll: RollCreate, db: Session = Depends(get_db)):
    """Создаёт новый рулон с заданными длиной и весом."""
    return create_roll(db, roll)


@app.delete("/rolls/{roll_id}", response_model=Roll)
def remove_roll(roll_id: int, db: Session = Depends(get_db)):
    """
    Удаляет рулон по ID (мягкое удаление).
    Возвращает 404, если рулон не найден или уже удалён.
    """
    roll = delete_roll(db, roll_id)
    if not roll:
        raise HTTPException(status_code=404, detail="Roll not found or already removed")
    return roll


@app.get("/rolls/", response_model=list[Roll])
def list_rolls(
    id_min: Optional[int] = None,
    id_max: Optional[int] = None,
    weight_min: Optional[float] = None,
    weight_max: Optional[float] = None,
    length_min: Optional[float] = None,
    length_max: Optional[float] = None,
    date_added_min: Optional[datetime] = None,
    date_added_max: Optional[datetime] = None,
    date_removed_min: Optional[datetime] = None,
    date_removed_max: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Возвращает список рулонов с возможностью фильтрации по различным параметрам
    (ID, вес, длина, даты добавления и удаления).
    """
    filters = {}
    if id_min is not None and id_max is not None:
        filters['id_range'] = (id_min, id_max)
    if weight_min is not None and weight_max is not None:
        filters['weight_range'] = (weight_min, weight_max)
    if length_min is not None and length_max is not None:
        filters['length_range'] = (length_min, length_max)
    if date_added_min is not None and date_added_max is not None:
        filters['date_added_range'] = (date_added_min, date_added_max)
    if date_removed_min is not None and date_removed_max is not None:
        filters['date_removed_range'] = (date_removed_min, date_removed_max)
    
    return get_rolls(db, **filters)


@app.get("/rolls/stats/", response_model=RollStats)
def get_statistics(start_date: datetime, end_date: datetime, db: Session = Depends(get_db)):
    """Возвращает статистику по рулонам за заданный период."""
    return get_roll_stats(db, start_date, end_date)