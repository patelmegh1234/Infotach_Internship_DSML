# Megh, Upload Date: 2026-07-28
# REST API Contract Unit Tests
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_contract() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "AcousticSpace API"
    assert "artifact_loaded" in payload


def test_demo_samples_contract() -> None:
    response = client.get("/api/demo-samples")
    assert response.status_code == 200
    demos = response.json()
    assert isinstance(demos, list)
    assert len(demos) > 0
    assert demos[0]["id"] == "authentic_speech"


def test_eda_summary_contract() -> None:
    response = client.get("/api/eda-summary")
    assert response.status_code == 200
    summary = response.json()
    assert "total_files" in summary
    assert "class_counts" in summary
