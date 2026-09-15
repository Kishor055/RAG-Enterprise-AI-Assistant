from abc import ABC, abstractmethod
from typing import Generator, Optional

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.2) -> str:
        """Generates a text completion given prompt and optional system instructions."""
        pass

    @abstractmethod
    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.2) -> Generator[str, None, None]:
        """Streams text completion tokens for real-time response rendering."""
        pass
