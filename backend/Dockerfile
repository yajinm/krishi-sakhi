# Multi-stage Dockerfile for Krishi Sakhi Backend
# Production-grade FastAPI application with Celery workers

# Base stage with common dependencies
FROM python:3.10-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    libspatialite-dev \
    libsqlite3-mod-spatialite \
    gdal-bin \
    proj-bin \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    libpng-dev \
    libopencv-dev \
    ffmpeg \
    espeak \
    espeak-data \
    libespeak1 \
    libespeak-dev \
    festival \
    festival-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/media /app/keys /app/logs

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to app user
USER appuser

# Expose port
EXPOSE 8000

# Default command for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# API stage
FROM base as api

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/media /app/keys /app/logs

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to app user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command for API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# Worker stage
FROM base as worker

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/media /app/keys /app/logs

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to app user
USER appuser

# Default command for worker (can be overridden)
CMD ["celery", "-A", "app.tasks.celery_app", "worker", "--loglevel=info"]

# Production stage
FROM base as production

# Install production dependencies only
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/media /app/keys /app/logs

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to app user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command for production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--access-log"]
