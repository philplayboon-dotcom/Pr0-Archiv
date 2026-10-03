from __future__ import annotations

import aiosqlite
from typing import Optional, Any
from contextlib import asynccontextmanager


class DatabaseConnection:
    """Manages aiosqlite connection with proper pragmas."""
    
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None
    
    async def connect(self) -> "DatabaseConnection":
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row
        # Set required pragmas per Konzept.md
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute("PRAGMA foreign_keys=ON")
        await self._conn.execute("PRAGMA busy_timeout=5000")
        await self._conn.execute("PRAGMA synchronous=NORMAL")
        return self
    
    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None
    
    async def __aenter__(self) -> "DatabaseConnection":
        return await self.connect()
    
    async def __aexit__(self, *exc_info) -> None:
        await self.close()
    
    async def execute(self, query: str, params: tuple = ()) -> Any:
        if not self._conn:
            raise RuntimeError("Database not connected. Call connect() first.")
        return await self._conn.execute(query, params)
    
    async def fetchone(self, query: str, params: tuple = ()) -> Optional[tuple]:
        if not self._conn:
            raise RuntimeError("Database not connected. Call connect() first.")
        cursor = await self._conn.execute(query, params)
        return await cursor.fetchone()
    
    async def fetchall(self, query: str, params: tuple = ()) -> list[tuple]:
        if not self._conn:
            raise RuntimeError("Database not connected. Call connect() first.")
        cursor = await self._conn.execute(query, params)
        return await cursor.fetchall()
    
    async def executemany(self, query: str, params_list: list[tuple]) -> Any:
        if not self._conn:
            raise RuntimeError("Database not connected. Call connect() first.")
        return await self._conn.executemany(query, params_list)
    
    async def executescript(self, sql_script: str) -> Any:
        if not self._conn:
            raise RuntimeError("Database not connected. Call connect() first.")
        return await self._conn.executescript(sql_script)
    
    async def commit(self) -> None:
        if self._conn:
            await self._conn.commit()
    
    async def rollback(self) -> None:
        if self._conn:
            await self._conn.rollback()
    
    def get_pool(self) -> aiosqlite.Connection:
        """Return raw connection for advanced usage."""
        return self._conn


async def get_database(db_path: str = "pr0archiv.db") -> DatabaseConnection:
    """Create and connect a database connection."""
    db = DatabaseConnection(db_path)
    await db.connect()
    return db