from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_dedupe_scenario(fresh_db, item_repo, collection_repo, item_collection_repo):
    """Test deduplication scenario.

    2 Items mit gleichem pr0_id aber verschiedenen PKs → nur PK in item_collection
    
    According to bugfix: If 2 items have the same pr0_id but different PKs,
    only the PK should appear in item_collection (not the pr0_id duplicate).
    """
    # 1. Insert 2 items with same pr0_id but different PKs
    item1 = await item_repo.create(pr0_id=999, post_url="http://item1.com")
    item2 = await item_repo.create(pr0_id=999, post_url="http://item2.com")
    
    assert item1.id != item2.id  # Different PKs
    assert item1.pr0_id == item2.pr0_id == 999  # Same pr0_id
    
    # 2. Create a collection
    col = await collection_repo.create(name="DedupColl")
    
    # 3. Add both items to collection
    # Each item_collection entry uses the item's PK (item1.id, item2.id)
    await item_collection_repo.add(item_id=item1.id, collection_id=col.id)
    await item_collection_repo.add(item_id=item2.id, collection_id=col.id)
    
    # 4. Verify: Both PKs are in item_collection (not pr0_id)
    links = await item_collection_repo.get_by_collection(col.id)
    assert len(links) == 2
    
    # Verify item_ids are the PKs, not pr0_id=999
    item_ids = {link["item_id"] for link in links}
    assert item1.id in item_ids
    assert item2.id in item_ids
    
    # CRITICAL: pr0_id=999 should NOT appear as item_id in item_collection
    assert 999 not in item_ids


async def test_add_and_get_by_collection(fresh_db, item_repo, collection_repo, item_collection_repo):
    """Test adding items and retrieving by collection."""
    item1 = await item_repo.create(pr0_id=100, post_url="http://1.com")
    item2 = await item_repo.create(pr0_id=200, post_url="http://2.com")
    col = await collection_repo.create(name="TestColl")
    
    await item_collection_repo.add(item_id=item1.id, collection_id=col.id)
    await item_collection_repo.add(item_id=item2.id, collection_id=col.id)
    
    links = await item_collection_repo.get_by_collection(col.id)
    assert len(links) == 2
    
    item_ids = {link["item_id"] for link in links}
    assert item1.id in item_ids
    assert item2.id in item_ids


async def test_remove_item_from_collection(fresh_db, item_repo, collection_repo, item_collection_repo):
    """Test removing item from collection."""
    item = await item_repo.create(pr0_id=300, post_url="http://3.com")
    col = await collection_repo.create(name="RemoveColl")
    
    await item_collection_repo.add(item_id=item.id, collection_id=col.id)
    links_before = await item_collection_repo.get_by_collection(col.id)
    assert len(links_before) == 1
    
    await item_collection_repo.remove(item_id=item.id, collection_id=col.id)
    links_after = await item_collection_repo.get_by_collection(col.id)
    assert len(links_after) == 0