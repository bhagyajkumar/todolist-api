from typing import Generator
import pytest
from app import app
from fastapi.testclient import TestClient
import os

os.environ["DATABASE_URL"] = "sqlite://:memory:"


client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_bad_token():
    response = client.get("/protected", headers={"Authorization": "Bearer bad-token"})
    assert response.status_code == 401

def test_create_user():
    response = client.post("/register", json={"username": "test", "password": "test"})
    assert response.status_code == 201