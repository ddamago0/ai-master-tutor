import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.study_material import StudyMaterialCreate, StudyMaterialResponse
from app.services.rag_engine import rag_engine
from app.services.user_service import get_or_create_default_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/ingest",
    response_model=StudyMaterialResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest study material extracted from LMS DOM or documents",
)
async def ingest_material(
    payload: StudyMaterialCreate,
    db: AsyncSession = Depends(get_db),
) -> StudyMaterialResponse:
    """
    Ingests, sanitizes, and indexes academic text into the vector database.
    Accepts raw payloads extracted by the browser extension (Moodle, Q10) or uploaded files.
    """
    try:
        # Resolve target student user
        if payload.user_id is None:
            user = await get_or_create_default_user(db)
            user_id = user.id
        else:
            user_id = payload.user_id

        # Clean text, compute dense vector embedding, and persist
        material = await rag_engine.index_study_material(
            db=db,
            user_id=user_id,
            title=payload.title,
            raw_content=payload.raw_content,
            source_type=payload.source_type,
            source_url=payload.source_url,
            metadata=payload.metadata,
        )

        return StudyMaterialResponse.model_validate(material)

    except Exception as err:
        logger.error("Failed to ingest study material: %s", err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while indexing study material: {str(err)}",
        )
