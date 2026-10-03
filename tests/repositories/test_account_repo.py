from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_create_account(fresh_db, account_repo):
    """Test creating an account."""
    acc = await account_repo.create(
        username="testuser",
        cookie_hash="hash123",
        display_name="Test User"
    )
    assert acc is not None
    assert acc.id is not None
    assert acc.username == "testuser"
    assert acc.cookie_hash == "hash123"
    assert acc.is_active is True


async def test_get_by_username(fresh_db, account_repo):
    """Test get_by_username returns correct account."""
    created = await account_repo.create(username="findme", cookie_hash="hash")
    found = await account_repo.get_by_username("findme")
    assert found is not None
    assert found.id == created.id
    assert found.username == "findme"


async def test_account_username_unique(fresh_db, account_repo):
    """Test UNIQUE constraint on account username."""
    await account_repo.create(username="uniqueuser", cookie_hash="hash1")
    try:
        await account_repo.create(username="uniqueuser", cookie_hash="hash2")
        assert False, "Should have raised UNIQUE constraint error"
    except Exception:
        pass  # Expected


async def test_get_active_accounts(fresh_db, account_repo):
    """Test get_active_accounts returns active accounts ordered by last_login."""
    await account_repo.create(username="user1", cookie_hash="h1", last_login="2026-01-01T10:00:00Z")
    await account_repo.create(username="user2", cookie_hash="h2", last_login="2026-01-01T12:00:00Z", is_active=False)
    await account_repo.create(username="user3", cookie_hash="h3", last_login="2026-01-01T11:00:00Z")
    
    active = await account_repo.get_active_accounts(limit=5)
    # Should only return active users, ordered by last_login DESC
    assert len(active) == 2
    assert active[0].username == "user3"  # Most recent login
    assert active[1].username == "user1"