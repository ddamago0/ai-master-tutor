import os
import uuid
import logging
from typing import Any, Dict, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.services.llm_gateway import llm_gateway

logger = logging.getLogger(__name__)


class SemanticCache:
    """
    Local semantic cache backed by ChromaDB.
    Caches Prompt -> Response pairs and performs cosine similarity search.
    If similarity >= 0.95, returns the cached LLM response, avoiding redundant API calls.
    """

    COLLECTION_NAME = "semantic_prompt_cache"

    def __init__(self, persist_directory: Optional[str] = None) -> None:
        self.persist_dir = persist_directory or settings.CHROMA_PERSIST_DIRECTORY
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # Initialize local persistent client
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        
        # Collection configured for cosine distance
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    async def get_cached_response(
        self,
        query: str,
        similarity_threshold: float = 0.95,
    ) -> Optional[str]:
        """
        Searches the semantic cache for a question similar to `query`.
        Returns the cached answer if cosine similarity >= similarity_threshold.
        """
        if not query or not query.strip():
            return None

        # Check if collection is empty
        if self.collection.count() == 0:
            return None

        try:
            # Generate 768-dim query embedding
            query_embedding = await llm_gateway.generate_embedding(query)

            # Query the nearest neighbor in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=1,
                include=["metadatas", "distances", "documents"],
            )

            distances = results.get("distances", [[]])
            metadatas = results.get("metadatas", [[]])

            if not distances or not distances[0] or not metadatas or not metadatas[0]:
                return None

            # With hnsw:space = "cosine", distance = 1 - cosine_similarity
            cosine_distance = distances[0][0]
            similarity = 1.0 - cosine_distance

            if similarity >= similarity_threshold:
                cached_answer = metadatas[0][0].get("response")
                logger.info(
                    "Semantic Cache HIT (similarity: %.4f >= %.2f) for query: '%s'",
                    similarity,
                    similarity_threshold,
                    query[:60],
                )
                return cached_answer

            logger.debug(
                "Semantic Cache MISS (best similarity: %.4f < %.2f)",
                similarity,
                similarity_threshold,
            )
            return None

        except Exception as err:
            logger.warning("Error querying semantic cache: %s", err)
            return None

    async def cache_response(
        self,
        query: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Stores a Query -> Response pair with its 768-dim embedding into ChromaDB.
        """
        if not query or not response:
            return

        try:
            query_embedding = await llm_gateway.generate_embedding(query)
            item_id = str(uuid.uuid4())

            entry_metadata: Dict[str, Any] = {
                "response": response,
                **(metadata or {}),
            }

            self.collection.add(
                ids=[item_id],
                embeddings=[query_embedding],
                documents=[query],
                metadatas=[entry_metadata],
            )
            logger.info("Successfully cached query-response pair: '%s'", query[:60])
        except Exception as err:
            logger.error("Failed to store entry in semantic cache: %s", err)


# Global instance
semantic_cache = SemanticCache()
