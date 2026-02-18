import json
import logging

from groq import AsyncGroq

from app.ai.base import LLMProvider

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = AsyncGroq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            completion = await self.client.chat.completions.create(
                messages=messages,
                model=self.model,
            )
            return completion.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            raise

    async def generate_structured(
        self,
        prompt: str,
        schema: dict,
        system_prompt: str = "",
        **kwargs,
    ) -> dict:
        structured_system = (
            f"{system_prompt}\n\n" if system_prompt else ""
        ) + (
            "You must respond with valid JSON only. No markdown, no explanation.\n"
            f"JSON schema:\n{json.dumps(schema, indent=2)}"
        )

        messages = [
            {"role": "system", "content": structured_system},
            {"role": "user", "content": prompt},
        ]

        try:
            completion = await self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                response_format={"type": "json_object"},
            )
            return json.loads(completion.choices[0].message.content or "{}")
        except Exception as e:
            logger.error(f"Groq structured generation failed: {e}")
            raise
