from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_collection_fk_uses_items_id_not_pr0_id(
    fresh_db, item_repo, collection_repo, item_collection_repo
):
    """TEST: ItemCollection FK must use items.id (PK), NOT pr0_id.
    
    Scenario:
    1. Insert Item → pr0_id=123, id=456 (auto-generated PK differs from pr0_id)
    2. Add to collection → item_collection.item_id = 456 (the PK)
    """
    # Step 1: Insert Item with pr0_id=123, auto-generated PK
    item = await item_repo.create(pr0_id=123, post_url="http://example.com")
    item_pk = item.id
    assert item_pk is not None
    
    # Step 2: Create collection
    col = await collection_repo.create(name="FKTestColl")
    col_id = col.id
    
    # Step 3: Add item to collection using items.id (PK)
    # THIS IS THE CORRECT USAGE - must use PK, NOT pr0_id
    await item_collection_repo.add(item_id=item_pk, collection_id=col_id)
    
    # Step 4: Verify the relationship uses PK (item_pk), not pr0_id (123)
    links = await item_collection_repo.get_by_collection(col_id)
    assert len(links) == 1
    
    # CRITICAL ASSERTION: item_id in item_collection must be item_pk (the PK)
    # NOT 123 (the pr0_id business key)
    assert links[0]["item_id"] == item_pk, \
        f"BUG: item_collection.item_id = {links[0]['item_id']}, should be {item_pk} (items.id/PK)"
    
    # Verify it's NOT pr0_id
    assert links[0]["item_id"] != 123, \
        "BUG: item_collection.item_id should NOT be pr0_id (123)"


async def test_dedupe_same_pr0_id_different_pks(
    fresh_db, item_repo, collection_repo, item_collection_repo
):
    """TEST: 2 Items mit gleichem pr0_id aber verschiedenen PKs → nur PK in item_collection.
    
    Scenario:
    - Item A: pr0_id=999, id=100 (PK)
    - Item B: pr0_id=999, id=200 (PK, different from A)
    - Both added to same collection
    - item_collection should have 2 entries with item_ids 100 and 200
    - NOT two entries with item_id=999 (pr0_id)
    """
    # Insert 2 items with same pr0_id but different PKs
    item_a = await item_repo.create(pr0_id=999, post_url="http://item-a.com")
    item_b = await item_repo.create(pr0_id=999, post_url="http://item-b.com")
    
    assert item_a.id != item_b.id, "Items should have different PKs"
    assert item_a.pr0_id == item_b.pr0_id == 999, "Items should have same pr0_id"
    
    # Create collection
    col = await collection_repo.create(name="DedupTest")
    col_id = col.id
    
    # Add both items to collection using their PKs
    await item_collection_repo.add(item_id=item_a.id, collection_id=col_id)
    await item_collection_repo.add(item_id=item_b.id, collection_id=col_id)
    
    # Verify both PKs are in item_collection
    links = await item_collection_repo.get_by_collection(col_id)
    assert len(links) == 2, f"Expected 2 links, got {len(links)}"
    
    item_ids = {link["item_id"] for link in links}
    assert item_a.id in item_ids, f"Expected {item_a.id} in item_collection"
    assert item_b.id in item_ids, f"Expected {item_b.id} in item_collection"
    
    # CRITICAL: pr0_id=999 should NOT appear as item_id in item_collection
    assert 999 not in item_ids, \
        "BUG: item_collection contains pr0_id=999 instead of PKs"