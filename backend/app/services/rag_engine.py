import uuid
import logging
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.study_material import StudyMaterial
from app.services.llm_gateway import llm_gateway
from app.services.text_processor import text_processor

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    RAG Engine that bridges pgvector dense vector retrieval with
    the zero-cost Google text-embedding-004 model.
    """

    @staticmethod
    async def search_relevant_materials(
        db: AsyncSession,
        query: str,
        user_id: Optional[uuid.UUID] = None,
        top_k: int = 5,
        min_similarity: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Generates query embedding and executes a cosine distance vector search
        over StudyMaterial records in PostgreSQL using pgvector.

        Args:
            db: Active async database session.
            query: User's question or search prompt.
            user_id: Optional user ID to isolate student knowledge base.
            top_k: Number of most relevant fragments to retrieve.
            min_similarity: Minimum cosine similarity score (0.0 to 1.0).

        Returns:
            List of dictionaries containing matching materials and similarity metrics.
        """
        if not query or not query.strip():
            return []

        # 1. Generate 768-dim query embedding using zero-cost Gemini model
        query_embedding = await llm_gateway.generate_embedding(query)

        # 2. Build pgvector cosine distance query
        distance_col = StudyMaterial.embedding.cosine_distance(query_embedding).label("distance")

        stmt = select(StudyMaterial, distance_col).where(
            StudyMaterial.embedding.is_not(None)
        )

        if user_id:
            stmt = stmt.where(StudyMaterial.user_id == user_id)

        stmt = stmt.order_by(distance_col).limit(top_k)

        # 3. Execute query
        result = await db.execute(stmt)
        rows = result.all()

        matches: List[Dict[str, Any]] = []
        for material, distance in rows:
            # Cosine similarity = 1 - cosine_distance
            similarity = 1.0 - float(distance)
            if similarity < min_similarity:
                continue

            matches.append({
                "material_id": str(material.id),
                "title": material.title,
                "content": material.cleaned_content or material.raw_content,
                "source_type": material.source_type,
                "source_url": material.source_url,
                "metadata": material.metadata_json,
                "similarity_score": round(similarity, 4),
            })

        return matches

    @staticmethod
    async def index_study_material(
        db: AsyncSession,
        user_id: uuid.UUID,
        title: str,
        raw_content: str,
        source_type: str = "manual",
        source_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StudyMaterial:
        """
        Sanitizes text, computes dense vector embedding, and persists
        the material into PostgreSQL.
        """
        cleaned_text = text_processor.clean_text(raw_content)
        
        # Compute embedding over representative text (first chunk/summary)
        embedding = await llm_gateway.generate_embedding(cleaned_text[:2000])

        material = StudyMaterial(
            user_id=user_id,
            title=title,
            source_type=source_type,
            source_url=source_url,
            raw_content=raw_content,
            cleaned_content=cleaned_text,
            embedding=embedding,
            metadata_json=metadata or {},
        )

        db.add(material)
        await db.commit()
        await db.refresh(material)
        return material


# Global instance
rag_engine = RAGEngine()
