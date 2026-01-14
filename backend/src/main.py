"""
FastAPI Application Entry Point

Phase 2 Todo Web Application Backend
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth import router as auth_router
from src.api.todos import router as todos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    yield
    # Shutdown


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Todo API",
        description="Phase 2 Todo Web Application Backend",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    allowed_origins = [origin.strip() for origin in frontend_url.split(",")]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    register_routes(app)

    return app


def register_routes(app: FastAPI) -> None:
    """Register all application routes."""
    # Include API routers
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(todos_router, prefix="/api/v1")

    @app.get("/", tags=["Health"])
    async def root():
        """Root endpoint - health check."""
        return {"status": "healthy", "service": "todo-api", "version": "0.1.0"}

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint for monitoring."""
        return {"status": "healthy", "service": "todo-api"}


# Create application instance
app = create_app()
