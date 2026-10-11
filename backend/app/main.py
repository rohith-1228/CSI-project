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

# Liveness Probe (root path /health)
@app.get("/health", response_model=HealthResponse, tags=["Status"])
async def health_check():
    """Liveness probe returning {"status": "ok"}."""
    return {"status": "ok"}

# Readiness Probe (root path /ready)
@app.get(
    "/ready",
    response_model=ReadyResponse,
    responses={
        200: {"description": "ML classifier and required model artifacts are loaded successfully."},
        503: {"description": "ML classifier or required model artifacts are not loaded."}
    },
    tags=["Status"]
)
async def readiness_check():
    """Readiness probe returning 200 only when ML classifier is loaded, otherwise 503."""
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

# Mount versioned API routes
app.include_router(api_router, prefix="/api/v1", tags=["Safety Assessment"])
