import pytest
from fastapi import status

def test_register_user(client):
    """Тест регистрации пользователя"""
    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "role_id": 3  # customer
    })
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "OK"

def test_login_user(client):
    """Тест входа пользователя"""
    # Сначала регистрируем
    client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "role_id": 3
    })
    
    # Пытаемся войти
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "access_token" in response.cookies