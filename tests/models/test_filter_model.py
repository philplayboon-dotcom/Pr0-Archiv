from __future__ import annotations

from core.models import Filter


class TestFilterModel:
    """Unit tests for Filter Pydantic model."""

    def test_filter_valid(self):
        """Test valid Filter creation."""
        f = Filter(id=1, name="NoNSFW", excluded_tags=["nsfw", "nsfl"])
        assert f.name == "NoNSFW"
        assert f.excluded_tags == ["nsfw", "nsfl"]

    def test_filter_excluded_tags_default(self):
        """Test excluded_tags defaults to empty list via property."""
        f = Filter(id=1, name="EmptyFilter")
        assert f.excluded_tags_list == []

    def test_filter_excluded_tags_none(self):
        """Test excluded_tags None returns empty list via property."""
        f = Filter(id=1, name="NoneFilter", excluded_tags=None)
        assert f.excluded_tags_list == []

    def test_filter_excluded_tags_string(self):
        """Test excluded_tags can be list of strings."""
        f = Filter(id=1, name="StringTags", excluded_tags=["tag1", "tag2"])
        assert f.excluded_tags_list == ["tag1", "tag2"]