import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api.v1.router import api_router

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager to initialize database extensions on startup."""
    try:
        logger.info("Initializing database and pgvector extension...")
        await init_db()
        logger.info("Database initialized successfully.")
    except Exception as err:
        logger.warning(
            "Could not automatically initialize DB at startup (PostgreSQL may be starting up): %s",
            err,
        )
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    lifespan=lifespan,
)

# CORS middleware for Next.js frontend and Chrome Extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits Web Client (localhost:3000) and chrome-extension:// origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register v1 API Routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "environment": settings.APP_ENV,
        "v1_docs": f"{settings.API_V1_PREFIX}/docs",
    }
