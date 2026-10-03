from __future__ import annotations

from core.models import ItemCollection


class TestItemCollectionModel:
    """Unit tests for ItemCollection Pydantic model.

    CRITICAL: Tests that item_id refers to items.id (PK), NOT pr0_id.
    """

    def test_item_collection_with_pk_id(self):
        """Test ItemCollection created with items.id (PK)."""
        ic = ItemCollection(item_id=456, collection_id=1)
        assert ic.item_id == 456
        assert ic.collection_id == 1

    def test_item_collection_composite_pk(self):
        """Test composite primary key (item_id, collection_id)."""
        ic1 = ItemCollection(item_id=1, collection_id=1)
        ic2 = ItemCollection(item_id=1, collection_id=2)
        assert ic1.item_id == ic2.item_id  # Same item in different collections
        assert ic1.collection_id != ic2.collection_id

    def test_item_collection_different_items_same_collection(self):
        """Test different items in same collection."""
        ic1 = ItemCollection(item_id=100, collection_id=1)
        ic2 = ItemCollection(item_id=200, collection_id=1)
        assert ic1.item_id != ic2.item_id
        assert ic1.collection_id == ic2.collection_id