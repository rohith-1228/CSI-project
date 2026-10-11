"""
CyberSaathi FastAPI Application Entry Point.
Production-ready web service for community cyber safety assessment.
"""

import logging
import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.security import SecurityHeadersMiddleware
from backend.app.ml.classifier import classifier
from backend.app.schemas.analysis import HealthResponse, ReadyResponse
from backend.app.api.endpoints import router as api_router

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("cybersaathi")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: loads ML models on startup and cleans up on shutdown."""
    logger.info("Initializing CyberSaathi service...")
    loaded = classifier.load()
    if loaded:
        logger.info(f"CyberSaathi ML classifier initialized successfully ({classifier.version}).")
    else:
        logger.warning("ML model could not be loaded from disk. Operating in heuristic rule fallback mode.")
    yield
    logger.info("Shutting down CyberSaathi service.")

app = FastAPI(
    title="CyberSaathi Safety Engine API",
    description="Community AI platform for scam detection, phishing link analysis, and community cyber protection.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Apply Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# Apply CORS Middleware
origins = settings.cors_origins_list
logger.info(f"Configuring CORS origins: {origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600
)

# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "Invalid input")
        errors.append(f"{field}: {msg}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "The submitted message could not be processed.",
            "details": errors
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing your request. Please try again shortly."
        }
    )

# Root route
@app.get("/", tags=["Status"])
async def root():
    return {
        "service": "CyberSaathi AI Safety Platform",
        "tagline": "Think before you click.",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready"
    }

# Liveness Probe
@app.get("/health", response_model=HealthResponse, tags=["Status"])
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        environment=settings.ENVIRONMENT
    )

# Readiness Probe
@app.get("/ready", response_model=ReadyResponse, tags=["Status"])
async def readiness_check() -> ReadyResponse:
    is_ready = classifier.is_loaded
    return ReadyResponse(
        status="ready" if is_ready else "degraded",
        model_loaded=is_ready,
        model_version=classifier.version,
        classifier_ready=is_ready,
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

# Mount versioned API routes
app.include_router(api_router, prefix="/api/v1", tags=["Safety Assessment"])
