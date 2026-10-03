from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.models import Item


class TestItemModel:
    """Unit tests for Item Pydantic model validation."""

    def test_item_valid_creation(self):
        """Test valid Item creation with all fields."""
        item = Item(
            id=1,
            pr0_id=12345,
            post_url="https://pr0gramm.com/post/12345",
            post_datetime="2026-01-01T12:00:00",
        )
        assert item.pr0_id == 12345
        assert item.user_rating is None
        assert item.user_tags == []

    def test_user_rating_validation_1(self):
        """Test user_rating lower bound (1)."""
        item = Item(id=1, pr0_id=1, user_rating=1)
        assert item.user_rating == 1

    def test_user_rating_validation_5(self):
        """Test user_rating upper bound (5)."""
        item = Item(id=1, pr0_id=1, user_rating=5)
        assert item.user_rating == 5

    def test_user_rating_invalid_0(self):
        """Test user_rating below 1 raises validation error."""
        try:
            Item(id=1, pr0_id=1, user_rating=0)
            assert False, "Should have raised ValidationError"
        except ValidationError:
            pass  # Expected

    def test_user_rating_invalid_6(self):
        """Test user_rating above 5 raises validation error."""
        try:
            Item(id=1, pr0_id=1, user_rating=6)
            assert False, "Should have raised ValidationError"
        except ValidationError:
            pass  # Expected

    def test_pr0_tags_string_to_list(self):
        """Test pr0_tags string conversion to list."""
        item = Item(id=1, pr0_id=1, pr0_tags="tag1, tag2, tag3")
        assert item.pr0_tags == ["tag1", "tag2", "tag3"]

    def test_pr0_tags_empty_string(self):
        """Test empty pr0_tags string becomes empty list."""
        item = Item(id=1, pr0_id=1, pr0_tags="")
        assert item.pr0_tags == []

    def test_user_tags_string_to_list(self):
        """Test user_tags string conversion to list."""
        item = Item(id=1, pr0_id=1, user_tags="mytag1, mytag2")
        assert item.user_tags == ["mytag1", "mytag2"]

    def test_item_json_serialization(self):
        """Test JSON serialization/deserialization for tags."""
        item = Item(id=1, pr0_id=1, pr0_tags=["tag1", "tag2"], user_tags=["usertag"])
        item_json = item.model_dump()
        assert "pr0_tags" in item_json
        assert item_json["pr0_tags"] == ["tag1", "tag2"]
        assert item_json["user_tags"] == ["usertag"]

    def test_content_type_validation(self):
        """Test content_type can be any string."""
        item = Item(id=1, pr0_id=1, content_type="video")
        assert item.content_type == "video"
        item2 = Item(id=2, pr0_id=2, content_type="image")
        assert item2.content_type == "image"