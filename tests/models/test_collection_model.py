from __future__ import annotations

from core.models import Collection


class TestCollectionModel:
    """Unit tests for Collection Pydantic model."""

    def test_collection_valid(self):
        """Test valid Collection creation."""
        col = Collection(id=1, name="TestCollection", description="A test collection")
        assert col.name == "TestCollection"
        assert col.description == "A test collection"

    def test_collection_minimal(self):
        """Test Collection with only required fields."""
        col = Collection(id=1, name="Minimal")
        assert col.name == "Minimal"
        assert col.description is None
        assert col.color is None
        assert col.created_at is None

    def test_collection_with_color(self):
        """Test Collection with color field."""
        col = Collection(id=1, name="Colored", color="#EE4D2D")
        assert col.color == "#EE4D2D"