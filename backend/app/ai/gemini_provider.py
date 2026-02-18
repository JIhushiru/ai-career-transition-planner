import json
import logging

from google import genai
from google.genai.types import GenerateContentConfig, GoogleSearch, Tool

from app.ai.base import LLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        use_search: bool = False,
        **kwargs,
    ) -> str:
        tools = []
        if use_search:
            tools.append(Tool(google_search=GoogleSearch()))

        config = GenerateContentConfig(
            system_instruction=system_prompt if system_prompt else None,
            tools=tools if tools else None,
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
            return response.text or ""
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise

    async def generate_structured(
        self,
        prompt: str,
        schema: dict,
        system_prompt: str = "",
        **kwargs,
    ) -> dict:
        structured_prompt = (
            f"{prompt}\n\n"
            f"Respond with valid JSON matching this schema:\n"
            f"{json.dumps(schema, indent=2)}"
        )

        config = GenerateContentConfig(
            system_instruction=system_prompt if system_prompt else None,
            response_mime_type="application/json",
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=structured_prompt,
                config=config,
            )
            return json.loads(response.text or "{}")
        except Exception as e:
            logger.error(f"Gemini structured generation failed: {e}")
            raise

    async def generate_with_search(self, prompt: str, system_prompt: str = "") -> dict:
        """Generate with Google Search grounding, returns text + sources."""
        config = GenerateContentConfig(
            system_instruction=system_prompt if system_prompt else None,
            tools=[Tool(google_search=GoogleSearch())],
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )

            sources = []
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                grounding = getattr(candidate, "grounding_metadata", None)
                if grounding:
                    chunks = getattr(grounding, "grounding_chunks", [])
                    for chunk in chunks or []:
                        web = getattr(chunk, "web", None)
                        if web:
                            sources.append({
                                "title": getattr(web, "title", ""),
                                "uri": getattr(web, "uri", ""),
                            })

            return {"text": response.text or "", "sources": sources}
        except Exception as e:
            logger.error(f"Gemini search generation failed: {e}")
            raise
