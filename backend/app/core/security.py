"""
CyberSaathi Security & Privacy Utilities.
Provides in-memory rate limiting, sensitive information redaction for logging,
and security headers middleware.
"""

import time
import re
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

logger = logging.getLogger("cybersaathi.security")

# Regex patterns for redacting sensitive PII from logs
REDACTION_PATTERNS = [
    (re.compile(r'\b\d{6}\b'), "[REDACTED_OTP]"),
    (re.compile(r'\b\d{10,12}\b'), "[REDACTED_PHONE]"),
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), "[REDACTED_EMAIL]"),
    (re.compile(r'\b(?:\d{4}[ -]?){3}\d{4}\b'), "[REDACTED_CARD]")
]

def redact_sensitive_data(text: str) -> str:
    """Masks OTPs, phone numbers, emails, and card numbers from log strings."""
    if not text:
        return ""
    masked = text
    for pattern, replacement in REDACTION_PATTERNS:
        masked = pattern.sub(replacement, masked)
    return masked

class RateLimiter:
    """In-memory sliding window rate limiter by client IP address."""
    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.requests = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - 60.0

        # Purge timestamps older than 60 seconds
        timestamps = [t for t in self.requests[client_ip] if t > window_start]
        self.requests[client_ip] = timestamps

        if len(timestamps) >= self.rpm:
            return False

        self.requests[client_ip].append(now)
        return True

    def reset(self):
        self.requests.clear()

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Applies strict security and privacy headers to all HTTP responses."""
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response
