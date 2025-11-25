# backend/tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_get_publications():
    response = client.get("/api/publications")
    assert response.status_code == 200
    assert isinstance(response.json(), list)