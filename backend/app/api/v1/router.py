from fastapi import APIRouter
from app.api.v1.endpoints import ingest, tutor, recall

api_router = APIRouter()

api_router.include_router(
    ingest.router,
    prefix="/materials",
    tags=["Study Materials"],
)
api_router.include_router(
    tutor.router,
    prefix="/tutor",
    tags=["AI Tutor"],
)
api_router.include_router(
    recall.router,
    prefix="/recall",
    tags=["Active Recall & SM-2"],
)
