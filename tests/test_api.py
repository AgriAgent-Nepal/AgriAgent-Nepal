from fastapi.testclient import TestClient

from agriagent.api import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_endpoint():
    response = client.post("/api/chat", json={"message": "Convert 1 ropani to hectare"})
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "area_conversion"
    assert "ha" in body["answer"]
