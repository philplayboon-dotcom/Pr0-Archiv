from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_set_and_get_value(fresh_db, settings_repo):
    """Test setting and getting a value."""
    await settings_repo.set_value("show_thumbnails", "true")
    value = await settings_repo.get_value("show_thumbnails")
    assert value == "true"


async def test_get_nonexistent_returns_default(fresh_db, settings_repo):
    """Test getting nonexistent key returns default."""
    value = await settings_repo.get_value("nonexistent", "default_value")
    assert value == "default_value"


async def test_update_existing_value(fresh_db, settings_repo):
    """Test updating an existing value."""
    await settings_repo.set_value("scan_limit", "1000")
    await settings_repo.set_value("scan_limit", "5000")
    value = await settings_repo.get_value("scan_limit")
    assert value == "5000"


async def test_list_settings(fresh_db, settings_repo):
    """Test listing all settings."""
    await settings_repo.set_value("key1", "val1")
    await settings_repo.set_value("key2", "val2")
    
    settings = await settings_repo.list()
    keys = {s.key for s in settings}
    assert "key1" in keys
    assert "key2" in keys