from __future__ import annotations

from abc import ABC
from typing import Protocol, TypeVar, Generic, Optional, Any

from pydantic import BaseModel

M = TypeVar("M", bound=BaseModel)


class RepositoryProtocol(Protocol[M]):
    """Base protocol for all repositories."""
    
    async def get(self, id: int) -> Optional[M]: ...
    async def list(self, **filters) -> list[M]: ...
    async def create(self, **data) -> M: ...
    async def update(self, id: int, **data) -> M: ...
    async def delete(self, id: int) -> None: ...
    async def exists(self, **filters) -> bool: ...


class BaseRepository(Generic[M], ABC):
    """Base class with common DB utility methods.
    
    Works with both DatabaseConnection wrapper and raw aiosqlite Connection.
    """
    
    def __init__(self, db) -> None:
        self.db = db
    
    async def _execute(self, query: str, params: tuple = ()) -> None:
        await self.db.execute(query, params)
    
    async def _fetch_one(self, query: str, params: tuple = ()) -> Optional[tuple]:
        """Fetch one row - works with both wrapper and raw aiosqlite connection."""
        # Try wrapper method first
        if hasattr(self.db, 'fetchone'):
            return await self.db.fetchone(query, params)
        # Fall back to raw aiosqlite connection
        cursor = await self.db.execute(query, params)
        return await cursor.fetchone()
    
    async def _fetch_all(self, query: str, params: tuple = ()) -> list[tuple]:
        """Fetch all rows - works with both wrapper and raw aiosqlite connection."""
        # Try wrapper method first
        if hasattr(self.db, 'fetchall'):
            return await self.db.fetchall(query, params)
        # Fall back to raw aiosqlite connection
        cursor = await self.db.execute(query, params)
        return await cursor.fetchall()