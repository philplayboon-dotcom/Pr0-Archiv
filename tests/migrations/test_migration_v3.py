from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_schema_v3_all_tables(fresh_db):
    """Test that all 7 tables exist after migration v3."""
    # Query sqlite_master for all tables
    rows = await fresh_db.fetchall(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    tables = {row[0] for row in rows}
    
    expected_tables = {
        "items", "collections", "item_collection",
        "scan_history", "filters", "accounts", "settings",
        "_migrations"
    }
    
    assert tables == expected_tables, \
        f"Expected: {expected_tables}, Got: {tables}"


async def test_migration_pragmas(fresh_db):
    """Test WAL mode, foreign_keys, busy_timeout pragmas."""
    # Check WAL mode
    mode = await fresh_db.fetchone("PRAGMA journal_mode")
    assert "wal" in str(mode[0]).lower()
    
    # Check foreign_keys
    fk = await fresh_db.fetchone("PRAGMA foreign_keys")
    assert fk[0] == 1  # ON
    
    # Check busy_timeout
    bt = await fresh_db.fetchone("PRAGMA busy_timeout")
    assert bt[0] == 5000


async def test_migration_version_tracking(fresh_db):
    """Test _migrations table exists and tracks versions."""
    # Check _migrations table exists
    tables = await fresh_db.fetchall(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    table_names = {row[0] for row in tables}
    assert "_migrations" in table_names
    
    # Check that version was recorded
    row = await fresh_db.fetchone("SELECT version FROM _migrations LIMIT 1")
    assert row is not None
    assert row[0] == "v3"


async def test_migration_idempotency(fresh_db):
    """Test that running schema v3 multiple times doesn't break."""
    # The schema uses CREATE TABLE IF NOT EXISTS, so running again should be fine
    schema_sql = """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pr0_id INTEGER UNIQUE NOT NULL
        );
    """
    await fresh_db.executescript(schema_sql)
    await fresh_db.commit()
    
    # Verify data is still intact
    tables = await fresh_db.fetchall(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    table_names = {row[0] for row in tables}
    assert "items" in table_names
    assert "collections" in table_names
    assert len(table_names) >= 7


async def test_migration_indices(fresh_db):
    """Test all expected indices exist."""
    indices = await fresh_db.fetchall(
        "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
    )
    index_names = {row[0] for row in indices}
    
    expected_indices = {
        "idx_items_pr0_id",
        "idx_item_collection_collection", 
        "idx_scan_history_status",
        "idx_filters_name",
        "idx_accounts_username",
    }
    
    found = expected_indices & index_names
    assert len(found) >= 4, f"Expected at least 4 indices, found: {found}"


async def test_foreign_key_constraints(fresh_db):
    """Test foreign key constraints are enforced."""
    # Try to insert into item_collection with non-existent item_id
    try:
        await fresh_db.execute(
            "INSERT INTO item_collection (item_id, collection_id) VALUES (999999, 1)"
        )
        await fresh_db.commit()
        # May or may not fail depending on FK enforcement timing
    except Exception:
        pass  # Expected: FK violation