from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from typing import Optional


class Filter(BaseModel):
    """Pydantic 2.x Model representing a Filter for exclusion tags."""
    
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    
    id: int
    name: str  # UNIQUE
    excluded_tags: Optional[list[str]] = Field(None, alias="excluded_tags")  # JSON Array
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @property
    def excluded_tags_list(self) -> list[str]:
        """Return excluded_tags as a list, defaulting to empty list if None."""
        return self.excluded_tags or []