import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.prompts import build_system_prompt
from app.schemas.tutor import (
    TutorQueryRequest,
    TutorQueryResponse,
    TutorSourceReference,
)
from app.services.llm_gateway import llm_gateway
from app.services.semantic_cache import semantic_cache
from app.services.rag_engine import rag_engine

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/ask",
    response_model=TutorQueryResponse,
    summary="Query the Universal Master Tutor with semantic caching and Corporation Mode RAG context",
)
async def ask_tutor(
    payload: TutorQueryRequest,
    db: AsyncSession = Depends(get_db),
) -> TutorQueryResponse:
    """
    Orchestrates the tutor pipeline:
    1. Semantic Cache check (ChromaDB cosine >= 0.95)
    2. Dense Vector Retrieval (PostgreSQL pgvector)
    3. Dynamic Prompt Assembly: Master Tutor Prompt + Student Profile + Corporation Mode context (role: system)
    4. Multi-model inference via LiteLLM Gateway
    5. Async persistence into semantic cache for subsequent queries
    """
    # Step 1: Semantic Cache Check
    if not payload.bypass_cache:
        cached_answer = await semantic_cache.get_cached_response(payload.query)
        if cached_answer:
            return TutorQueryResponse(
                answer=cached_answer,
                cached=True,
                cache_type="semantic",
                sources=[],
            )

    # Step 2: Dense Vector Retrieval (RAG Context from Study Materials)
    relevant_sources = await rag_engine.search_relevant_materials(
        db=db,
        query=payload.query,
        user_id=payload.user_id,
        top_k=payload.top_k_context,
    )

    # Format context passages
    context_passages: List[str] = []
    sources_summary: List[TutorSourceReference] = []

    if relevant_sources:
        for src in relevant_sources:
            context_passages.append(
                f"[DOCUMENTO: {src['title']} | ORIGEN: {src['source_type'].upper()}]\n{src['content']}"
            )
            sources_summary.append(
                TutorSourceReference(
                    material_id=src["material_id"],
                    title=src["title"],
                    source_type=src["source_type"],
                    similarity_score=src["similarity_score"],
                )
            )

    formatted_rag_text = "\n\n".join(context_passages)

    # Step 3: Compose Dynamic System Prompt with Corporation Mode injection
    system_prompt = build_system_prompt(rag_context=formatted_rag_text)

    # Messages array aligned with LiteLLM: system role has prompt+RAG, user has query
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": payload.query},
    ]

    # Step 4: Inference via Zero-Cost LLM Gateway (Groq -> Gemini -> Cohere)
    try:
        answer = await llm_gateway.generate_text(
            messages=messages,
            temperature=0.4,
            max_tokens=1024,
        )
    except Exception as err:
        logger.error("LLM Gateway generation failed: %s", err)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Inference engine unavailable: {str(err)}",
        )

    # Step 5: Save newly generated answer into ChromaDB Semantic Cache
    try:
        await semantic_cache.cache_response(
            query=payload.query,
            response=answer,
            metadata={"source_count": len(sources_summary)},
        )
    except Exception as cache_err:
        logger.warning("Failed to store query in semantic cache: %s", cache_err)

    return TutorQueryResponse(
        answer=answer,
        cached=False,
        cache_type=None,
        sources=sources_summary,
    )
