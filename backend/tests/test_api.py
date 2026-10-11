"""Integration tests for CyberSaathi FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.api.endpoints import rate_limiter

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_rate_limit():
    rate_limiter.reset()

def test_health_endpoint_root():
    """Requirement 3 & 5: GET /health at root path returns {"status": "ok"}."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_health_endpoint_api_prefix():
    """GET /api/v1/health also returns {"status": "ok"}."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_ready_endpoint_success_when_loaded():
    """Requirement 4: GET /ready returns 200 when ML classifier is loaded."""
    from backend.app.ml.classifier import classifier
    classifier.load()
    assert classifier.is_loaded is True

    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["model_loaded"] is True
    assert "model_version" in data

def test_ready_endpoint_503_when_not_loaded():
    """Requirement 4: GET /ready returns 503 when ML classifier is not loaded."""
    from backend.app.ml.classifier import classifier
    original_loaded = classifier._is_loaded
    original_pipeline = classifier.pipeline

    try:
        # Simulate classifier failure to load
        classifier._is_loaded = False
        classifier.pipeline = None

        response = client.get("/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "not_ready"
        assert data["model_loaded"] is False
        assert "error" in data
    finally:
        # Restore classifier state
        classifier._is_loaded = original_loaded
        classifier.pipeline = original_pipeline

def test_root_advertises_health_and_ready():
    """Root endpoint / advertises /health and /ready routes."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["health"] == "/health"
    assert data["ready"] == "/ready"

def test_info_endpoint():
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "privacy_policy_summary" in data

def test_analyze_empty_message():
    # Empty message should be rejected with 422
    response = client.post("/api/v1/analyze", json={"message": ""})
    assert response.status_code == 422

def test_analyze_whitespace_message():
    response = client.post("/api/v1/analyze", json={"message": "    "})
    assert response.status_code == 422

def test_analyze_oversized_message():
    huge_message = "A" * 5500
    response = client.post("/api/v1/analyze", json={"message": huge_message})
    assert response.status_code == 422

def test_analyze_scam_message_success():
    payload = {
        "message": "Dear customer, your SBI account is suspended today. Update your PAN card immediately at http://sbi-kyc-verify.xyz"
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "likely_scam"
    assert data["risk_level"] == "high"
    assert len(data["reasons"]) > 0
    assert "recommended_action" in data
    assert "disclaimer" in data
    assert "analyzed_features" in data

def test_analyze_safe_message_success():
    payload = {
        "message": "Hi, let's meet tomorrow at 10 AM in the college library for group study."
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "likely_safe"
    assert data["risk_level"] == "low"

def test_security_headers_present():
    response = client.get("/health")
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert "referrer-policy" in response.headers

def test_cors_preflight():
    response = client.options(
        "/api/v1/analyze",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST"
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"

def test_rate_limiting():
    # Temporarily set a very low limit to test rate limiting
    orig_rpm = rate_limiter.rpm
    rate_limiter.rpm = 3
    try:
        payload = {"message": "Hello are we meeting today for coffee?"}
        for _ in range(3):
            r = client.post("/api/v1/analyze", json=payload)
            assert r.status_code == 200
        # 4th request should trigger 429
        r4 = client.post("/api/v1/analyze", json=payload)
        assert r4.status_code == 429
        assert "Rate limit exceeded" in r4.json()["detail"]
    finally:
        rate_limiter.rpm = orig_rpm
        rate_limiter.reset()
