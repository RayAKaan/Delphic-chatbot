from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_conversations_endpoint_greeting() -> None:
    response = client.post(
        "/api/v1/conversations/test",
        json={"whatsapp_number": "+919000000001", "intent": "GREETING"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["state"] == "WELCOME"
    assert body["handoff_required"] is False
    assert "Welcome" in body["message"]


def test_conversations_endpoint_find_job_with_entities() -> None:
    response = client.post(
        "/api/v1/conversations/test",
        json={
            "whatsapp_number": "+919000000001",
            "intent": "FIND_JOB",
            "entities": {"location": "Bangalore", "experience": "FRESHER"},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["state"] == "SEARCHING_JOBS"
    assert len(body["jobs"]) > 0


def test_conversations_endpoint_handoff() -> None:
    response = client.post(
        "/api/v1/conversations/test",
        json={"whatsapp_number": "+919000000001", "intent": "HUMAN_SUPPORT"},
    )
    assert response.status_code == 200
    assert response.json()["handoff_required"] is True


def test_conversations_endpoint_rejects_wrong_token() -> None:
    response = client.post(
        "/api/v1/conversations/test",
        json={"whatsapp_number": "+919000000001", "intent": "NOT_AN_INTENT"},
    )
    assert response.status_code == 422
