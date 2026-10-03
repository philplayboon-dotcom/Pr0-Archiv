from __future__ import annotations

from typing import Optional, List
from core.models import Settings
from core.repositories.base import RepositoryProtocol, BaseRepository


class SettingsRepositoryProtocol(RepositoryProtocol[Settings]):
    """Protocol defining Settings repository interface."""
    
    async def get_value(self, key: str, default: str = "") -> str: ...
    async def set_value(self, key: str, value: str) -> Settings: ...


class SettingsRepository(BaseRepository[Settings], SettingsRepositoryProtocol):
    """aiosqlite implementation of Settings repository."""
    
    async def get(self, id: int) -> Optional[Settings]:
        # Settings uses key as PK, not integer ID
        return None
    
    async def list(self, **filters) -> list[Settings]:
        query = "SELECT * FROM settings"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if key == "key":
                    conditions.append("key LIKE ?")
                    params.append(f"%{value}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        rows = await self._fetch_all(query, tuple(params))
        return [Settings.model_validate(dict(row)) for row in rows]
    
    async def create(self, **data) -> Settings:
        query = "INSERT INTO settings (key, value) VALUES (?, ?)"
        await self._execute(query, (data["key"], data["value"]))
        return Settings(key=data["key"], value=data["value"])
    
    async def update(self, id: int, **data) -> Settings:
        # Settings uses key as PK
        key = data.pop("key", None)
        if not key:
            key = list(data.keys())[0]  # fallback
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        params = tuple(data.values()) + (key,)
        query = f"UPDATE settings SET {set_clause} WHERE key = ?"
        await self._execute(query, params)
        return Settings(key=key, value=data.get("value", ""))
    
    async def delete(self, id: int) -> None:
        # Not used for key-value
        pass
    
    async def exists(self, **filters) -> bool:
        query = "SELECT 1 FROM settings WHERE 1=1"
        params = []
        for key, value in filters.items():
            query += f" AND {key} = ?"
            params.append(value)
        row = await self._fetch_one(query, tuple(params))
        return row is not None
    
    async def get_value(self, key: str, default: str = "") -> str:
        query = "SELECT value FROM settings WHERE key = ?"
        row = await self._fetch_one(query, (key,))
        return row[0] if row else default
    
    async def set_value(self, key: str, value: str) -> Settings:
        query = "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)"
        await self._execute(query, (key, value))
        return Settings(key=key, value=value)