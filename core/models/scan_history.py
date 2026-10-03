from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from typing import Optional


class ScanHistory(BaseModel):
    """Pydantic 2.x Model representing a Scan run."""
    
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    
    id: int
    scan_type: str  # initial / incremental / backfill
    status: str  # running / completed / failed
    started_at: str
    completed_at: Optional[str] = None
    oldest_pr0_id: Optional[int] = None
    newest_pr0_id: Optional[int] = None
    fetched_count: Optional[int] = None
    new_count: Optional[int] = None
    duplicate_count: Optional[int] = None
    error_message: Optional[str] = None
    config_snapshot: Optional[dict] = Field(None, alias="config_snapshot")