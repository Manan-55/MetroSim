from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import time
import uuid
from typing import Dict, Any

from app.config import settings
from app.database import engine, Base
from app.core.auth import get_current_user
from app.utils.logger import app_logger, get_logger
from app.api import trains, analytics, optimization, simulation

# Import all models to ensure they're registered with SQLAlchemy
from app.models import user, train, track, schedule

logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Train Management System")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Train Management System")

# Create FastAPI application
app = FastAPI(
    title="Train Management System",
    description="Advanced train scheduling, optimization, and analytics platform",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests and responses"""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    logger.info(
        f"Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None
        }
    )
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(
            f"Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time": round(process_time, 4)
            }
        )
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(round(process_time, 4))
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed",
            extra={
                "request_id": request_id,
                "error": str(e),
                "process_time": round(process_time, 4)
            }
        )
        raise

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.warning(
        f"HTTP exception",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "request_id": request_id,
            "timestamp": time.time()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.error(
        f"Unhandled exception",
        extra={
            "request_id": request_id,
            "error": str(exc),
            "type": type(exc).__name__
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request_id,
            "timestamp": time.time()
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Train Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Protected endpoint example
@app.get("/protected")
async def protected_endpoint(current_user = Depends(get_current_user)):
    """Example protected endpoint"""
    return {
        "message": f"Hello {current_user.username}",
        "user_id": current_user.id,
        "role": current_user.role
    }

# Include API routers
app.include_router(
    trains.router,
    prefix="/api/v1/trains",
    tags=["trains"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["analytics"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    optimization.router,
    prefix="/api/v1/optimization",
    tags=["optimization"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    simulation.router,
    prefix="/api/v1/simulation",
    tags=["simulation"],
    dependencies=[Depends(get_current_user)]
)

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Keep connection alive and handle real-time updates
            data = await websocket.receive_text()
            logger.info(f"WebSocket message received: {data}")
            
            # Echo back for now - implement real-time features as needed
            await websocket.send_text(f"Echo: {data}")
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("WebSocket connection closed")

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
