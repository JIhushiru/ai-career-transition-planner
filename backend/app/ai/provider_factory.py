import logging

from app.ai.base import LLMProvider
from app.ai.gemini_provider import GeminiProvider
from app.ai.groq_provider import GroqProvider
from app.config import settings

logger = logging.getLogger(__name__)


class ProviderFactory:
    """Select AI provider based on task type.

    Strategy:
    - Tasks requiring web search / grounding -> Gemini (primary)
    - Fast reasoning without search -> Groq (fallback)
    - If primary fails -> automatic fallback to secondary
    """

    @staticmethod
    def get_provider(task_type: str = "default") -> LLMProvider:
        if task_type in ("search", "grounded", "market_data", "resources"):
            if settings.gemini_api_key:
                return GeminiProvider(settings.gemini_api_key)
            logger.warning("Gemini API key not set, falling back to Groq")
            return GroqProvider(settings.groq_api_key)

        if task_type in ("reasoning", "fast", "extraction"):
            if settings.groq_api_key:
                return GroqProvider(settings.groq_api_key)
            logger.warning("Groq API key not set, falling back to Gemini")
            return GeminiProvider(settings.gemini_api_key)

        # Default: Gemini primary
        if settings.gemini_api_key:
            return GeminiProvider(settings.gemini_api_key)
        if settings.groq_api_key:
            return GroqProvider(settings.groq_api_key)
        raise RuntimeError("No AI provider API keys configured")


def get_gemini_provider() -> GeminiProvider:
    return GeminiProvider(settings.gemini_api_key)


def get_groq_provider() -> GroqProvider:
    return GroqProvider(settings.groq_api_key)
