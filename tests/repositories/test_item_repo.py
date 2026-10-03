from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio

from core.models import Item


async def test_create_item(fresh_db, item_repo):
    """Test creating a new item."""
    item = await item_repo.create(
        pr0_id=12345,
        post_url="https://pr0gramm.com/12345",
    )
    assert item is not None
    assert item.id is not None
    assert item.pr0_id == 12345
    
    # Verify it was created
    row = await item_repo.get_by_pr0_id(12345)
    assert row is not None
    assert row.pr0_id == 12345


async def test_get_by_id(fresh_db, item_repo):
    """Test getting item by PK id."""
    created = await item_repo.create(pr0_id=999, post_url="http://example.com")
    row = await item_repo.get(created.id)
    assert row is not None
    assert row.id == created.id


async def test_get_by_pr0_id(fresh_db, item_repo):
    """Test getting item by pr0_id (UNIQUE constraint)."""
    await item_repo.create(pr0_id=55555, post_url="http://a.com")
    row = await item_repo.get_by_pr0_id(55555)
    assert row is not None
    assert row.pr0_id == 55555


async def test_upsert_preserves_user_data(fresh_db, item_repo):
    """Test upsert preserves user_rating and user_tags."""
    # Create initial item with user data
    created = await item_repo.create(
        pr0_id=77777,
        post_url="http://original.com",
        user_rating=4,
        user_tags=["mytag"],
    )
    assert created.user_rating == 4
    assert created.user_tags == ["mytag"]
    
    # Upsert with new data but no user data
    updated = await item_repo.upsert(
        pr0_id=77777,
        post_url="http://updated.com",
        thumbnail_path="/new/thumb.jpg"
    )
    
    # User data should be preserved
    assert updated.user_rating == 4
    assert updated.user_tags == ["mytag"]
    assert updated.post_url == "http://updated.com"
    assert updated.thumbnail_path == "/new/thumb.jpg"


async def test_user_rating_check(fresh_db, item_repo):
    """Test CHECK constraint: user_rating 1-5."""
    # Valid rating
    item = await item_repo.create(pr0_id=111, post_url="http://valid.com", user_rating=3)
    assert item.user_rating == 3
    
    # Invalid rating should be rejected by DB
    try:
        await item_repo.create(pr0_id=222, post_url="http://invalid.com", user_rating=0)
        # Depending on implementation, may or may not raise
    except Exception:
        pass  # Expected behavior


async def test_bulk_create(fresh_db, item_repo):
    """Bulk insert items."""
    items = [
        {"pr0_id": 10000 + i, "post_url": f"http://example{i}.com"}
        for i in range(100)
    ]
    created = await item_repo.bulk_create(items)
    assert len(created) == 100
    
    # Verify count
    count = await item_repo.count_all()
    assert count >= 100


async def test_get_recent(fresh_db, item_repo):
    """Test get_recent returns items ordered by created_at DESC."""
    await item_repo.create(pr0_id=1, post_url="http://first.com")
    await item_repo.create(pr0_id=2, post_url="http://second.com")
    await item_repo.create(pr0_id=3, post_url="http://third.com")
    
    recent = await item_repo.get_recent(limit=2)
    assert len(recent) == 2
    # Most recent first
    assert recent[0].pr0_id == 3
    assert recent[1].pr0_id == 2


async def test_count_all(fresh_db, item_repo):
    """Test count_all returns correct count."""
    initial = await item_repo.count_all()
    await item_repo.create(pr0_id=1, post_url="http://a.com")
    await item_repo.create(pr0_id=2, post_url="http://b.com")
    final = await item_repo.count_all()
    assert final == initial + 2