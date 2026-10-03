from __future__ import annotations

from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict
from typing import Optional


class Item(BaseModel):
    """Pydantic 2.x Model representing a pr0 Item."""
    
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    
    id: int
    pr0_id: int = Field(..., alias="pr0_id")
    post_url: Optional[str] = None
    post_datetime: Optional[str] = None
    scan_datetime: Optional[str] = None
    thumbnail_path: Optional[str] = None
    content_type: Optional[str] = Field(None, alias="content_type")  # video, video_audio, image, gif
    content_path: Optional[str] = None
    pr0_tags: list[str] = Field(default_factory=list, alias="pr0_tags")  # JSON array
    user_rating: Optional[int] = None  # 1-5
    user_tags: list[str] = Field(default_factory=list, alias="user_tags")  # JSON array
    user_last_rated_at: Optional[str] = None
    
    @field_validator("user_rating")
    @classmethod
    def rating_must_be_between_1_and_5(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 1 or v > 5):
            raise ValueError("user_rating must be between 1 and 5")
        return v
    
    @field_validator("pr0_tags", mode="before")
    @classmethod
    def pr0_tags_must_be_list(cls, v: Optional[str | list]) -> Optional[list]:
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(",") if tag.strip()]
        return v or []
    
    @field_validator("user_tags", mode="before")
    @classmethod
    def user_tags_must_be_list(cls, v: Optional[str | list]) -> Optional[list]:
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(",") if tag.strip()]
        return v or []