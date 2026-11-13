from fastapi.testclient import TestClient

from src.app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_hello_defaults_to_world():
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_hello_accepts_name_query():
    response = client.get("/hello", params={"name": "Alice"})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Alice!"}


def test_echo_returns_message_and_length():
    response = client.post("/echo", json={"message": "hello"})
    assert response.status_code == 200
    assert response.json() == {"echoed": "hello", "length": 5}


def test_echo_rejects_empty_message():
    response = client.post("/echo", json={"message": ""})
    assert response.status_code == 422


def test_echo_rejects_missing_field():
    response = client.post("/echo", json={})
    assert response.status_code == 422
