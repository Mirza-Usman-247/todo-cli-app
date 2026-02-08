"""
FastAPI Application Entry Point

Phase 2-5 Todo Web Application Backend
- Phase 2-4: Auth, Todos, Chat (existing)
- Phase 5: Event-Driven Architecture with Kafka and Dapr (NEW)
"""

import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Existing Phase 2-4 routers
from src.api.auth import router as auth_router
from src.api.todos import router as todos_router
from src.api.chat import router as chat_router

# Phase 5: Event-driven Tasks API
try:
    from src.api.tasks_events import router as tasks_events_router
    TASKS_EVENTS_ENABLED = True
except ImportError:
    TASKS_EVENTS_ENABLED = False
    tasks_events_router = None
    print("⚠️  Event-driven tasks API not available")

# Phase 5: Dapr integration
try:
    from dapr.ext.fastapi import DaprApp
    from src.events.subscribers import handle_event
    DAPR_ENABLED = True
except ImportError:
    DAPR_ENABLED = False
    handle_event = None
    print("⚠️  Dapr SDK not installed - Phase 5 event features disabled")

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting Todo Application Backend...")
    logger.info(f"   Phase 2-4: Auth, Todos, Chat ✅")
    if DAPR_ENABLED:
        logger.info(f"   Phase 5: Event-Driven (Dapr) ✅")
        logger.info(f"   Dapr HTTP Port: {os.getenv('DAPR_HTTP_PORT', '3500')}")
    yield
    # Shutdown
    logger.info("👋 Shutting down Todo Backend...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Todo API",
        description="Multi-Phase Todo Web Application Backend with Event-Driven Architecture",
        version="5.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Phase 5: Initialize Dapr app and register event subscribers if available
    if DAPR_ENABLED:
        dapr_app = DaprApp(app)
        register_event_subscribers(dapr_app)
        logger.info("✅ Dapr app initialized for event-driven features")

    # Configure CORS
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    allowed_origins = [origin.strip() for origin in frontend_url.split(",")]

    # Log CORS configuration for debugging
    print(f"🔧 CORS Configuration:")
    print(f"   FRONTEND_URL env: {frontend_url}")
    print(f"   Allowed origins: {allowed_origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Register routes
    register_routes(app)

    return app


def register_event_subscribers(dapr_app: "DaprApp") -> None:
    """Register Dapr Pub/Sub event subscribers."""
    if not DAPR_ENABLED or not handle_event:
        return

    # Subscribe to todo-created events
    @dapr_app.subscribe(pubsub="pubsub-kafka", topic="todo-created")
    async def on_todo_created(event_data):
        """Handle todo-created events from Kafka"""
        logger.info("📩 Received todo-created event")
        await handle_event("todo-created", event_data)

    # Subscribe to todo-updated events
    @dapr_app.subscribe(pubsub="pubsub-kafka", topic="todo-updated")
    async def on_todo_updated(event_data):
        """Handle todo-updated events from Kafka"""
        logger.info("📩 Received todo-updated event")
        await handle_event("todo-updated", event_data)

    # Subscribe to todo-deleted events
    @dapr_app.subscribe(pubsub="pubsub-kafka", topic="todo-deleted")
    async def on_todo_deleted(event_data):
        """Handle todo-deleted events from Kafka"""
        logger.info("📩 Received todo-deleted event")
        await handle_event("todo-deleted", event_data)

    # Subscribe to todo-reminder events
    @dapr_app.subscribe(pubsub="pubsub-kafka", topic="todo-reminder")
    async def on_todo_reminder(event_data):
        """Handle todo-reminder events from Kafka"""
        logger.info("📩 Received todo-reminder event")
        await handle_event("todo-reminder", event_data)

    logger.info("✅ Registered 4 event subscribers: todo-created, todo-updated, todo-deleted, todo-reminder")


def register_routes(app: FastAPI) -> None:
    """Register all application routes."""
    # Include API routers (Phase 2-4 existing functionality)
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(todos_router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")

    # Phase 5: Event-driven tasks API
    if TASKS_EVENTS_ENABLED and tasks_events_router:
        app.include_router(tasks_events_router, prefix="/api/v1")
        logger.info("✅ Registered event-driven tasks API at /api/v1/events/tasks")

    @app.get("/", tags=["Health"])
    async def root():
        """Root endpoint - health check."""
        return {
            "status": "healthy",
            "service": "todo-api",
            "version": "5.0.0",
            "phases": {
                "phase2_4": "Auth, Todos, Chat",
                "phase5": "Event-Driven Architecture" if DAPR_ENABLED else "Disabled"
            }
        }

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint for monitoring."""
        return {
            "status": "healthy",
            "service": "todo-api",
            "dapr_enabled": DAPR_ENABLED,
            "components": ["pubsub-kafka", "statestore-redis"] if DAPR_ENABLED else []
        }

    @app.get("/debug/cors", tags=["Debug"])
    async def debug_cors():
        """Debug CORS configuration."""
        frontend_url = os.getenv("FRONTEND_URL", "NOT_SET")
        allowed_origins = [origin.strip() for origin in frontend_url.split(",")]
        return {
            "frontend_url_env": frontend_url,
            "allowed_origins": allowed_origins,
            "environment": os.getenv("ENVIRONMENT", "NOT_SET"),
        }


# Create application instance
app = create_app()
