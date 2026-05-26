"""Loads .env and exposes all settings as a Config dataclass."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    openai_api_key: str
    openai_model: str
    max_tokens: int
    temperature: float
    output_dir: Path

    @classmethod
    def from_env(cls) -> "Config":
        """Build Config from environment variables. Raises if required vars are missing."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_key_here":
            raise EnvironmentError(
                "OPENAI_API_KEY is not set. Add your key to the .env file."
            )

        model = os.getenv("OPENAI_MODEL")
        if not model:
            raise EnvironmentError("OPENAI_MODEL is not set in .env.")

        try:
            max_tokens = int(os.getenv("MAX_TOKENS", "400"))
        except ValueError:
            raise EnvironmentError("MAX_TOKENS must be an integer in .env.")

        try:
            temperature = float(os.getenv("TEMPERATURE", "0.1"))
        except ValueError:
            raise EnvironmentError("TEMPERATURE must be a float in .env.")

        output_dir = Path(os.getenv("OUTPUT_DIR", "output"))
        output_dir.mkdir(parents=True, exist_ok=True)

        return cls(
            openai_api_key=api_key,
            openai_model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            output_dir=output_dir,
        )
