# Тесты для проверки маршрутов API с использованием тестовой базы данных SQLite в памяти.

import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from main import app


# Добавляем корневую директорию проекта в sys.path для корректного импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Создаём новый Base для тестов, чтобы изолировать тестовую базу данных
Base = declarative_base()

# Импортируем модель Roll для регистрации в тестовом Base
from models import Roll

# Настройка тестовой базы данных SQLite в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция для переопределения зависимости get_db в тестах
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Применяем переопределение зависимости для FastAPI
app.dependency_overrides[override_get_db] = override_get_db

# Фикстура для создания и удаления таблиц перед и после тестов
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Инициализируем тестовый клиент FastAPI
client = TestClient(app)


def test_create_roll():
    """Тест создания нового рулона через POST /rolls/."""
    response = client.post("/rolls/", json={"length": 10.5, "weight": 20.0})
    assert response.status_code == 200
    assert response.json()["length"] == 10.5
    assert response.json()["weight"] == 20.0


def test_get_rolls():
    """Тест получения списка рулонов через GET /rolls/."""
    client.post("/rolls/", json={"length": 10.5, "weight": 20.0})
    response = client.get("/rolls/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_delete_roll():
    """Тест удаления рулона через DELETE /rolls/{roll_id}."""
    create_response = client.post("/rolls/", json={"length": 10.5, "weight": 20.0})
    roll_id = create_response.json()["id"]
    response = client.delete(f"/rolls/{roll_id}")
    assert response.status_code == 200
    assert response.json()["id"] == roll_id