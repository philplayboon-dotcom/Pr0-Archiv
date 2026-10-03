from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from typing import Optional


class Account(BaseModel):
    """Pydantic 2.x Model representing a User Account with Cookie."""
    
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    
    id: int
    username: str
    display_name: Optional[str] = None
    cookie_hash: str  # Hash of the pp= cookie value
    last_login: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None