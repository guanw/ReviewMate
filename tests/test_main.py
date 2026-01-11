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
    response = client.post("/analyze-diff", json={"diff": "another diff", "pr_url": "https://github.com/sample/repo/pull/123"})
    assert response.status_code == 200

def test_cors_headers():
    # Test OPTIONS preflight
    response = client.options("/analyze-diff", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

def test_agent_workflow_quality():
    # Test quality agent detects naming issues
    diff = "+ def calculateTotal(items):\n+     pass"
    response = client.post("/analyze-diff", json={"diff": diff})
    assert response.status_code == 200
    result = response.json()["message"]
    assert "calculateTotal" in result  # Should flag camelCase

def test_agent_workflow_performance():
    # Test performance agent detects nested loops
    diff = "+ for i in range(10):\n+     for j in range(10):\n+         for k in range(10):\n+             pass"
    response = client.post("/analyze-diff", json={"diff": diff})
    assert response.status_code == 200
    result = response.json()["message"]
    assert "nested loops" in result.lower()

