import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_analyze_diff_valid():
    response = client.post("/analyze-diff", json={"diff": "test diff content"})
    assert response.status_code == 200
    assert "Suggestions:" in response.json()["message"]

def test_analyze_diff_empty():
    response = client.post("/analyze-diff", json={"diff": ""})
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]

def test_analyze_diff_with_pr_url():
    response = client.post("/analyze-diff", json={"diff": "another diff", "pr_url": "https://github.com/test/pr"})
    assert response.status_code == 200