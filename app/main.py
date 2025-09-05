
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.db import init_db, close_db
from app.otel import setup_otel
from app.routers import (
    auth,
    farmers,
    activities,
    advisories,
    reminders,
    kb,
    convo,
    ext,
    admin,
    privacy,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting Krishi Sakhi API...")
    
    # Initialize database
    await init_db()
    
    # Setup OpenTelemetry
    if settings.otel_exporter_otlp_endpoint:
        setup_otel()
    
    # Create media directory
    settings.media_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ Krishi Sakhi API started successfully!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Krishi Sakhi API...")
    await close_db()
    print("✅ Krishi Sakhi API shut down successfully!")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Personal Farming Assistant for Kerala Farmers",
    version=settings.app_version,
    docs_url="/docs" if settings.enable_swagger_ui else None,
    redoc_url="/redoc" if settings.enable_redoc else None,
    openapi_url="/openapi.json" if settings.enable_swagger_ui else None,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["localhost", "127.0.0.1"],
)

# Add static files
app.mount("/media", StaticFiles(directory=str(settings.media_path)), name="media")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(farmers.router, prefix="/farmers", tags=["Farmers"])
app.include_router(activities.router, prefix="/activities", tags=["Activities"])
app.include_router(advisories.router, prefix="/advisories", tags=["Advisories"])
app.include_router(reminders.router, prefix="/reminders", tags=["Reminders"])
app.include_router(kb.router, prefix="/kb", tags=["Knowledge Base"])
app.include_router(convo.router, prefix="/convo", tags=["Conversation"])
app.include_router(ext.router, prefix="/ext", tags=["External Data"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(privacy.router, prefix="/privacy", tags=["Privacy"])


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "HTTPException",
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation exceptions."""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": 422,
                "message": "Validation error",
                "type": "ValidationError",
                "details": exc.errors(),
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    if settings.debug:
        import traceback
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": str(exc),
                    "type": "InternalServerError",
                    "traceback": traceback.format_exc(),
                }
            },
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": "Internal server error",
                    "type": "InternalServerError",
                }
            },
        )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Krishi Sakhi API",
        "version": settings.app_version,
        "docs": "/docs" if settings.enable_swagger_ui else None,
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    from app.db import check_db_health
    
    db_healthy = await check_db_health()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "version": settings.app_version,
        "database": "healthy" if db_healthy else "unhealthy",
        "timestamp": asyncio.get_event_loop().time(),
    }


@app.get("/metrics", tags=["Metrics"])
async def metrics():
    """Metrics endpoint for monitoring."""
    if not settings.enable_metrics:
        return {"error": "Metrics disabled"}
    
    # This would integrate with Prometheus or other metrics systems
    return {
        "uptime": asyncio.get_event_loop().time(),
        "version": settings.app_version,
        "environment": "development" if settings.debug else "production",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
