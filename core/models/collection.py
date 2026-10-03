from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from typing import Optional


class Collection(BaseModel):
    """Pydantic 2.x Model representing a Collection."""
    
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    
    id: int
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    created_at: Optional[str] = None