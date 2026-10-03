from __future__ import annotations

from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict


class Settings(BaseModel):
    """Pydantic 2.x Model representing Application Settings (key-value)."""
    
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    
    key: str  # PK
    value: str  # e.g. show_thumbnails, scan_limit, theme
    
    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Settings key must not be empty")
        return v.strip()