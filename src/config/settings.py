"""Central configuration loader for the project.

This is a small, explicit Settings class used by the G12 refactor.
It reads environment variables (and optionally a .env file) and exposes
attributes for use as `from src.config.settings import settings`.

Keep this file minimal and dependency-free. If you prefer pydantic,
we can replace this with `pydantic.BaseSettings` later.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional


class Settings:
    def __init__(
        self, env_file: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None
    ):
        # Optionally load a .env file if provided
        if env_file:
            p = Path(env_file)
            if p.exists():
                try:
                    from dotenv import load_dotenv

                    load_dotenv(dotenv_path=str(p))
                except Exception:
                    # dotenv is optional; ignore if not installed
                    pass

        o = overrides or {}

        # Core variables discovered by scan (add more as needed)
        self.OLLAMA_HOST: str = o.get("OLLAMA_HOST") or os.getenv(
            "OLLAMA_HOST", "http://localhost:11434"
        )
        self.AIDER_ENDPOINT: str = o.get("AIDER_ENDPOINT") or os.getenv(
            "AIDER_ENDPOINT", "http://localhost:8000"
        )
        self.LESSON_PATH: str = o.get("LESSON_PATH") or os.getenv(
            "LESSON_PATH", "data/lessons"
        )
        self.MODEL_NAME: str = o.get("MODEL_NAME") or os.getenv("MODEL_NAME", "mistral")
        self.DB_URL: Optional[str] = o.get("DB_URL") or os.getenv("DB_URL")
        self.LOG_LEVEL: str = o.get("LOG_LEVEL") or os.getenv("LOG_LEVEL", "INFO")
        self.IGNORED_DIRS: List[str] = o.get("IGNORED_DIRS") or os.getenv(
            "IGNORED_DIRS", "history,.venv,venv,site-packages"
        ).split(",")
        self.MAX_TOKENS: int = int(
            o.get("MAX_TOKENS") or os.getenv("MAX_TOKENS", "2048")
        )

    def get(self, name: str, default: Any = None) -> Any:
        return getattr(self, name, os.getenv(name, default))


# single shared settings instance
settings = Settings()
