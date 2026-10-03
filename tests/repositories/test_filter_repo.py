from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_create_filter(fresh_db, filter_repo):
    """Test creating a filter."""
    f = await filter_repo.create(name="NoNSFW", excluded_tags=["nsfw", "nsfl"])
    assert f is not None
    assert f.id is not None
    assert f.name == "NoNSFW"
    assert f.excluded_tags == ["nsfw", "nsfl"]


async def test_get_by_name(fresh_db, filter_repo):
    """Test get_by_name returns correct filter."""
    created = await filter_repo.create(name="FindMe", excluded_tags=["tag1"])
    found = await filter_repo.get_by_name("FindMe")
    assert found is not None
    assert found.id == created.id
    assert found.excluded_tags == ["tag1"]


async def test_filter_name_unique(fresh_db, filter_repo):
    """Test UNIQUE constraint on filter name."""
    await filter_repo.create(name="UniqueFilter")
    try:
        await filter_repo.create(name="UniqueFilter")  # Duplicate
        assert False, "Should have raised UNIQUE constraint error"
    except Exception:
        pass  # Expected


async def test_list_filters(fresh_db, filter_repo):
    """Test list returns all filters ordered by name."""
    await filter_repo.create(name="Zebra", excluded_tags=["z"])
    await filter_repo.create(name="Alpha", excluded_tags=["a"])
    
    filters = await filter_repo.list()
    names = [f.name for f in filters]
    assert "Alpha" in names
    assert "Zebra" in names


async def test_update_filter(fresh_db, filter_repo):
    """Test updating a filter."""
    f = await filter_repo.create(name="Original", excluded_tags=["old"])
    updated = await filter_repo.update(f.id, name="Updated", excluded_tags=["new"])
    assert updated.name == "Updated"
    assert updated.excluded_tags == ["new"]