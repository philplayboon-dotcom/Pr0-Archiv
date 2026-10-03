from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class ItemCollection(BaseModel):
    """Pydantic 2.x Model representing the Item-Collection junction table.
    
    CRITICAL: item_id references items.id (PK), NOT items.pr0_id (Business Key).
    This ensures proper deduplication: 2 Items with same pr0_id but different PKs
    can both exist in item_collection via their distinct PKs.
    """
    
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    
    item_id: int  # FK → items.id (PK), NOT pr0_id
    collection_id: int  # FK → collections.id