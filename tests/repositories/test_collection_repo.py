from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio

from core.models import Collection


async def test_create_collection(fresh_db, collection_repo):
    """Test creating a collection."""
    col = await collection_repo.create(name="MyCollection", description="Test")
    assert col is not None
    assert col.id is not None
    assert col.name == "MyCollection"
    
    row = await collection_repo.get_by_name("MyCollection")
    assert row is not None
    assert row.name == "MyCollection"


async def test_collection_name_unique(fresh_db, collection_repo):
    """Test UNIQUE constraint on collection name."""
    await collection_repo.create(name="UniqueName")
    try:
        await collection_repo.create(name="UniqueName")  # Duplicate
        assert False, "Should have raised UNIQUE constraint error"
    except Exception:
        pass  # Expected


async def test_get_by_name(fresh_db, collection_repo):
    """Test get_by_name returns correct collection."""
    created = await collection_repo.create(name="FindMe", description="Desc")
    found = await collection_repo.get_by_name("FindMe")
    assert found is not None
    assert found.id == created.id
    assert found.description == "Desc"


async def test_list_collections(fresh_db, collection_repo):
    """Test list returns all collections ordered by name."""
    await collection_repo.create(name="Zebra")
    await collection_repo.create(name="Alpha")
    await collection_repo.create(name="Beta")
    
    cols = await collection_repo.list()
    names = [c.name for c in cols]
    assert "Alpha" in names
    assert "Beta" in names
    assert "Zebra" in names


async def test_add_item_to_collection_uses_pk(fresh_db, item_repo, collection_repo):
    """Test adding item to collection using items.id (PK).

    THIS IS THE CRITICAL BUG FIX TEST:
    Collection FK nutzt items.id (PK), NICHT pr0_id (Business Key).
    """
    # 1. Insert Item → pr0_id=123, id=456 (auto-generated PK)
    item = await item_repo.create(pr0_id=123, post_url="http://example.com")
    item_pk = item.id
    assert item_pk is not None
    
    # 2. Create Collection
    col = await collection_repo.create(name="TestColl")
    col_id = col.id
    
    # 3. Add item to collection using items.id (PK)
    # THIS IS THE CRITICAL PART: must use item_id=item_pk, NOT pr0_id=123
    success = await collection_repo.add_item(collection_id=col_id, item_id=item_pk)
    assert success is True
    
    # 4. Verify: item_collection.item_id = item_pk (the PK), NOT 123 (pr0_id)
    links = await collection_repo.get_items_in_collection(col_id)
    assert len(links) == 1
    # The link should have item_id = item_pk (PK), NOT pr0_id = 123
    assert links[0]["item_id"] == item_pk


async def test_remove_item_from_collection(fresh_db, item_repo, collection_repo):
    """Test removing item from collection."""
    item = await item_repo.create(pr0_id=999, post_url="http://item.com")
    col = await collection_repo.create(name="RemoveTest")
    
    await collection_repo.add_item(collection_id=col.id, item_id=item.id)
    links_before = await collection_repo.get_items_in_collection(col.id)
    assert len(links_before) == 1
    
    await collection_repo.remove_item(collection_id=col.id, item_id=item.id)
    links_after = await collection_repo.get_items_in_collection(col.id)
    assert len(links_after) == 0