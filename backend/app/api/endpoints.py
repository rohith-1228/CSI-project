"""
CyberSaathi REST API Endpoints.
Houses the primary analysis endpoint and information metadata routes.
"""

import logging
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
from backend.app.schemas.analysis import (
    AnalyzeRequest, AnalyzeResponse, ServiceInfoResponse, HealthResponse, ReadyResponse
)
from backend.app.services.safety_engine import assess_safety
from backend.app.ml.classifier import classifier
from backend.app.core.security import RateLimiter
from backend.app.core.config import settings

logger = logging.getLogger("cybersaathi.api")
router = APIRouter()
rate_limiter = RateLimiter(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)

def get_client_ip(request: Request) -> str:
    """Extracts client IP respecting proxy headers."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze suspicious message or URL",
    description="Evaluates an SMS, WhatsApp forward, email text, or URL for scam and phishing risk indicators."
)
async def analyze_message(payload: AnalyzeRequest, request: Request) -> AnalyzeResponse:
    client_ip = get_client_ip(request)

    # 1. Check rate limit
    if not rate_limiter.is_allowed(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait a minute before checking another message."
        )

    # 2. Length check beyond pydantic
    if len(payload.message) > settings.MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Message is too long. Maximum allowed length is {settings.MAX_MESSAGE_LENGTH} characters."
        )

    # 3. Assess safety using engine
    try:
        result = assess_safety(payload.message)
        # Log metadata only, never the submitted message contents
        logger.info(
            f"Analysis completed: client_ip={client_ip}, length={len(payload.message)}, "
            f"verdict={result.verdict.value}, urls_count={len(result.analyzed_features.urls_found)}"
        )
        return result
    except Exception as e:
        logger.error(f"Error during safety analysis: {str(e)}", exc_info=False)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while analyzing the message. Please try again."
        )

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check (API prefix)",
    description="Liveness probe returning {'status': 'ok'}."
)
async def api_health_check() -> HealthResponse:
    return HealthResponse(status="ok")

@router.get(
    "/ready",
    response_model=ReadyResponse,
    responses={
        200: {"description": "ML classifier and required model artifacts are loaded successfully."},
        503: {"description": "ML classifier or required model artifacts are not loaded."}
    },
    summary="Readiness check (API prefix)",
    description="Returns HTTP 200 when ML classifier is operational; otherwise HTTP 503."
)
async def api_readiness_check():
    if classifier.is_loaded:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ready",
                "model_loaded": True,
                "model_version": classifier.version
            }
        )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "not_ready",
            "model_loaded": False,
            "error": "ML classifier or required model artifacts are not loaded."
        }
    )

@router.get(
    "/info",
    response_model=ServiceInfoResponse,
    summary="CyberSaathi Service Information",
    description="Returns public service metadata and privacy policy guarantees."
)
async def get_service_info() -> ServiceInfoResponse:
    return ServiceInfoResponse(
        name="CyberSaathi Cyber Safety Engine",
        version="1.0.0",
        description="Public-service AI platform to detect scams, phishing links, and deceptive messages.",
        documentation_url="/docs",
        privacy_policy_summary="Zero-retention architecture. Messages submitted for analysis are processed in memory and never stored, logged, or shared."
    )
