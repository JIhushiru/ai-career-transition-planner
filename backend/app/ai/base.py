from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        pass

    @abstractmethod
    async def generate_structured(self, prompt: str, schema: dict, **kwargs) -> dict:
        pass
