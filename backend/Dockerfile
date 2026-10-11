# Dockerfile for CyberSaathi FastAPI Backend
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency definition and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code, models, and data
COPY app/ ./app/
COPY ../models /models
COPY ../data /data

# Create non-privileged user for security
RUN useradd -m -u 1000 cybersaathi && chown -R cybersaathi:cybersaathi /app
USER cybersaathi

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Production start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
