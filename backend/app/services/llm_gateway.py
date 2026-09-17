import logging
from typing import Any, Dict, List, Optional
import litellm
from litellm import Router, Cache
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure LiteLLM native local in-memory exact cache
# Avoids redundant API calls if exact prompt hash is matched
litellm.cache = Cache(type="local")
litellm.telemetry = False


class LLMGateway:
    """
    Zero-Cost LLM Gateway utilizing LiteLLM with multi-provider fallback
    and exact response caching.

    Fallback Priority:
      1. Primary (Speed): Groq (Llama 3.1 8B / 70B)
      2. Fallback 1 (Context Window): Google AI Studio (Gemini 1.5 Flash)
      3. Fallback 2 (Redundancy): Cohere (Command-R)
    """

    PRIMARY_MODEL = "groq/llama-3.1-8b-instant"
    FALLBACK_MODEL_1 = "gemini/gemini-1.5-flash"
    FALLBACK_MODEL_2 = "cohere/command-r"
    EMBEDDING_MODEL = "gemini/text-embedding-004"

    def __init__(self) -> None:
        self._setup_router()

    def _setup_router(self) -> None:
        """Configures LiteLLM router with explicit model fallbacks."""
        model_list = [
            {
                "model_name": "primary-generator",
                "litellm_params": {
                    "model": self.PRIMARY_MODEL,
                    "api_key": settings.GROQ_API_KEY,
                },
            },
            {
                "model_name": "fallback-1",
                "litellm_params": {
                    "model": self.FALLBACK_MODEL_1,
                    "api_key": settings.GEMINI_API_KEY,
                },
            },
            {
                "model_name": "fallback-2",
                "litellm_params": {
                    "model": self.FALLBACK_MODEL_2,
                    "api_key": settings.COHERE_API_KEY,
                },
            },
        ]

        # LiteLLM router manages healthy deployments, retries, and fallbacks
        self.router = Router(
            model_list=model_list,
            fallbacks=[{"primary-generator": ["fallback-1", "fallback-2"]}],
            cache_responses=True,
            timeout=30.0,
            num_retries=1,
        )

    async def generate_text(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        """
        Asynchronously generates text applying fallback rules and exact caching.

        Args:
            messages: List of chat messages, e.g. [{"role": "user", "content": "..."}]
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Extra parameters passed to completion

        Returns:
            The generated response text as a string.
        """
        try:
            # First attempt through configured router with automatic fallback
            response = await self.router.acompletion(
                model="primary-generator",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                caching=True,
                **kwargs,
            )
            return response.choices[0].message.content or ""
        except Exception as err:
            logger.warning(
                "Router completion failed or partially degraded: %s. Attempting explicit direct fallback chain.",
                err,
            )
            # Direct fallback sequence guarantee if router instance encounters unhandled errors
            fallback_chain = [
                (self.FALLBACK_MODEL_1, settings.GEMINI_API_KEY),
                (self.FALLBACK_MODEL_2, settings.COHERE_API_KEY),
            ]
            for model_name, api_key in fallback_chain:
                if not api_key:
                    continue
                try:
                    direct_response = await litellm.acompletion(
                        model=model_name,
                        messages=messages,
                        api_key=api_key,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        caching=True,
                        **kwargs,
                    )
                    return direct_response.choices[0].message.content or ""
                except Exception as direct_err:
                    logger.error("Direct fallback to %s failed: %s", model_name, direct_err)
                    continue

            raise RuntimeError(
                f"All zero-cost LLM providers failed to generate text. Last error: {err}"
            ) from err

    async def generate_embedding(
        self,
        text: str,
        **kwargs: Any,
    ) -> List[float]:
        """
        Generates 768-dimensional embeddings exclusively using Google AI Studio
        (gemini/text-embedding-004) under the zero-cost tier.

        Args:
            text: Input text string to embed.

        Returns:
            A list of 768 float values representing the dense semantic vector.
        """
        if not text or not text.strip():
            raise ValueError("Input text for embedding cannot be empty.")

        try:
            response = await litellm.aembedding(
                model=self.EMBEDDING_MODEL,
                input=[text],
                api_key=settings.GEMINI_API_KEY,
                caching=True,
                **kwargs,
            )
            embedding = response.data[0]["embedding"]
            return embedding
        except Exception as err:
            logger.error("Failed to generate embedding with %s: %s", self.EMBEDDING_MODEL, err)
            raise RuntimeError(
                f"Embedding generation failed using {self.EMBEDDING_MODEL}: {err}"
            ) from err


# Export singleton instance
llm_gateway = LLMGateway()
