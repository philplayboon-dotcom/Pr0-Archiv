from __future__ import annotations

from core.database.connection import DatabaseConnection


SCHEMA_V3_SQL = """
-- 1. items table
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
    user_last_rated_at TEXT
);

-- Index for pr0_id lookups (Business Key)
CREATE INDEX IF NOT EXISTS idx_items_pr0_id ON items(pr0_id);

-- 2. collections table
CREATE TABLE IF NOT EXISTS collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    color TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- 3. item_collection junction table
-- BUGFIX: Uses items.id (PK) NOT items.pr0_id (Business Key)
CREATE TABLE IF NOT EXISTS item_collection (
    item_id INTEGER NOT NULL,
    collection_id INTEGER NOT NULL,
    PRIMARY KEY (item_id, collection_id),
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
);

-- 4. scan_history table
CREATE TABLE IF NOT EXISTS scan_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'running',
    started_at TEXT NOT NULL,
    completed_at TEXT,
    oldest_pr0_id INTEGER,
    newest_pr0_id INTEGER,
    fetched_count INTEGER NOT NULL DEFAULT 0,
    new_count INTEGER NOT NULL DEFAULT 0,
    duplicate_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    config_snapshot JSON NOT NULL DEFAULT '{}'
);

-- 5. filters table
CREATE TABLE IF NOT EXISTS filters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    excluded_tags JSON NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- 6. accounts table
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    display_name TEXT,
    cookie_hash TEXT NOT NULL,
    last_login TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- 7. settings table (key-value store)
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY NOT NULL,
    value TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Migration tracking table
CREATE TABLE IF NOT EXISTS _migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Index for common queries
CREATE INDEX IF NOT EXISTS idx_item_collection_collection ON item_collection(collection_id);
CREATE INDEX IF NOT EXISTS idx_scan_history_status ON scan_history(status);
CREATE INDEX IF NOT EXISTS idx_filters_name ON filters(name);
CREATE INDEX IF NOT EXISTS idx_accounts_username ON accounts(username);
"""


class MigrationManager:
    """Manages database schema migrations."""
    
    def __init__(self, conn: DatabaseConnection) -> None:
        self.conn = conn
    
    async def get_current_version(self) -> str:
        """Check current schema version from metadata table."""
        # Create metadata table if not exists
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS _migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL UNIQUE,
                applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
            )
        """)
        await self.conn.commit()
        
        row = await self.conn.fetchone(
            "SELECT version FROM _migrations ORDER BY id DESC LIMIT 1"
        )
        return row[0] if row else "0"
    
    async def apply_migrations(self, target_version: str = "v3") -> None:
        """Apply pending migrations up to target version."""
        current = await self.get_current_version()
        
        versions = ["v1", "v2", "v3"]
        start_idx = 0
        if current in versions:
            start_idx = versions.index(current) + 1
        
        for version in versions[start_idx:]:
            if version == "v1":
                await self._apply_v1()
            elif version == "v2":
                await self._apply_v2()
            elif version == "v3":
                await self._apply_v3()
            
            # Record migration
            await self.conn.execute(
                "INSERT OR IGNORE INTO _migrations (version, applied_at) VALUES (?, datetime('now'))",
                (version,)
            )
            await self.conn.commit()
            print(f"Applied migration {version}")
            
            if version == target_version:
                break
    
    async def _apply_v1(self) -> None:
        """Initial schema - items table."""
        sql = """
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
            user_last_rated_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_items_pr0_id ON items(pr0_id);
        """
        await self.conn.executescript(sql)
        await self.conn.commit()
    
    async def _apply_v2(self) -> None:
        """Add collections, accounts, settings tables."""
        sql = """
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            color TEXT,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        );
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            display_name TEXT,
            cookie_hash TEXT NOT NULL,
            last_login TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        );
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY NOT NULL,
            value TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        );
        CREATE TABLE IF NOT EXISTS item_collection (
            item_id INTEGER NOT NULL,
            collection_id INTEGER NOT NULL,
            PRIMARY KEY (item_id, collection_id),
            FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
            FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
        );
        """
        await self.conn.executescript(sql)
        await self.conn.commit()
    
    async def _apply_v3(self) -> None:
        """Full Schema v3 - all 7 tables + indices + pragmas."""
        await self.conn.executescript(SCHEMA_V3_SQL)
        await self.conn.commit()
        
        # Enable required pragmas
        await self.conn.execute("PRAGMA journal_mode=WAL")
        await self.conn.execute("PRAGMA foreign_keys=ON")
        await self.conn.execute("PRAGMA busy_timeout=5000")
        await self.conn.execute("PRAGMA synchronous=NORMAL")