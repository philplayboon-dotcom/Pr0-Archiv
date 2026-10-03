from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import aiosqlite
import pytest
import pytest_asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def tmp_db_path():
    """Temporary database path for the test session."""
    tmp = Path(tempfile.mkdtemp()) / "test.db"
    yield tmp
    # Cleanup after session
    if tmp.exists():
        tmp.unlink()
        # Also remove WAL/SHM files
        for suffix in ["-wal", "-shm"]:
            wal_file = tmp.with_suffix(tmp.suffix + suffix)
            if wal_file.exists():
                wal_file.unlink()


@ pytest_asyncio.fixture(scope="function")
async def db_connection(tmp_db_path):
    """Async SQLite connection with Phase 1 pragmas."""
    conn = await aiosqlite.connect(str(tmp_db_path))
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA foreign_keys=ON")
    await conn.execute("PRAGMA busy_timeout=5000")
    await conn.commit()
    yield conn
    await conn.close()


async def apply_schema_v3(conn: aiosqlite.Connection):
    """Apply Schema v3 to the database."""
    schema_sql = """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pr0_id INTEGER UNIQUE NOT NULL,
            post_url TEXT,
            post_datetime TEXT,
            scan_datetime TEXT,
            thumbnail_path TEXT,
            content_type TEXT,
            content_path TEXT,
            pr0_tags JSON NOT NULL DEFAULT '[]',
            user_rating INTEGER CHECK(user_rating BETWEEN 1 AND 5),
            user_last_rated_at TEXT,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        );
        
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            color TEXT,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        );
        
        CREATE TABLE IF NOT EXISTS item_collection (
            item_id INTEGER NOT NULL,
            collection_id INTEGER NOT NULL,
            PRIMARY KEY (item_id, collection_id),
            FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
            FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_type TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'running',
            started_at TEXT NOT NULL,
            completed_at TEXT,
            oldest_pr0_id INTEGER,
            newest_pr0_id INTEGER,
            fetched_count INTEGER DEFAULT 0,
            new_count INTEGER DEFAULT 0,
            duplicate_count INTEGER DEFAULT 0,
            error_message TEXT,
            config_snapshot JSON NOT NULL DEFAULT '{}'
        );
        
        CREATE TABLE IF NOT EXISTS filters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            excluded_tags JSON NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        );
        
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            display_name TEXT,
            cookie_hash TEXT NOT NULL,
            last_login TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        );
        
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        );
        
        CREATE TABLE IF NOT EXISTS _migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL UNIQUE,
            applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        );
        
        -- Indizes
        CREATE INDEX IF NOT EXISTS idx_items_pr0_id ON items(pr0_id);
        CREATE INDEX IF NOT EXISTS idx_item_collection_collection ON item_collection(collection_id);
        CREATE INDEX IF NOT EXISTS idx_scan_history_status ON scan_history(status);
        CREATE INDEX IF NOT EXISTS idx_filters_name ON filters(name);
        CREATE INDEX IF NOT EXISTS idx_accounts_username ON accounts(username);
    """
    await conn.executescript(schema_sql)
    await conn.commit()
    
    # Record migration
    await conn.execute(
        "INSERT OR IGNORE INTO _migrations (version) VALUES (?)",
        ("v3",)
    )
    await conn.commit()


@ pytest_asyncio.fixture(scope="function")
async def fresh_db(db_connection):
    """Fresh database with schema v3 (7 tables + indices + pragmas)."""
    await apply_schema_v3(db_connection)
    yield db_connection
    # Rollback after each test to keep isolation
    await db_connection.rollback()


# Repository fixtures (sync fixtures that depend on async fixture)
@ pytest_asyncio.fixture
async def item_repo(fresh_db):
    from core.repositories import ItemRepository
    return ItemRepository(fresh_db)


@ pytest_asyncio.fixture
async def collection_repo(fresh_db):
    from core.repositories import CollectionRepository
    return CollectionRepository(fresh_db)


@ pytest_asyncio.fixture
async def item_collection_repo(fresh_db):
    from core.repositories import ItemCollectionRepository
    return ItemCollectionRepository(fresh_db)


@ pytest_asyncio.fixture
async def scan_history_repo(fresh_db):
    from core.repositories import ScanHistoryRepository
    return ScanHistoryRepository(fresh_db)


@ pytest_asyncio.fixture
async def filter_repo(fresh_db):
    from core.repositories import FilterRepository
    return FilterRepository(fresh_db)


@ pytest_asyncio.fixture
async def account_repo(fresh_db):
    from core.repositories import AccountRepository
    return AccountRepository(fresh_db)


@ pytest_asyncio.fixture
async def settings_repo(fresh_db):
    from core.repositories import SettingsRepository
    return SettingsRepository(fresh_db)