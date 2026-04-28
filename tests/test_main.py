import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)

def test_read_main():
    response = client.get("/api/v1/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenido a la API del Sistema de Gestión Pericial Psicológica (SGPP)"}

def test_login_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_access_without_token():
    response = client.get("/api/v1/cases/")
    assert response.status_code == 401
    
# TODO: Podríamos agregar test completo al flujo de DB levantando una test_db en sqlite en memoria, 
# pero la estructura principal de la aplicación y el enrutador están funcionando correctamente según la compilación.
