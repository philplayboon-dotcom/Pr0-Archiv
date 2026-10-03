from __future__ import annotations

from typing import Optional, List
from core.models import Filter
from core.repositories.base import RepositoryProtocol, BaseRepository


class FilterRepositoryProtocol(RepositoryProtocol[Filter]):
    """Protocol defining Filter repository interface."""
    
    async def get_by_name(self, name: str) -> Optional[Filter]: ...


class FilterRepository(BaseRepository[Filter], FilterRepositoryProtocol):
    """aiosqlite implementation of Filter repository."""
    
    async def get(self, id: int) -> Optional[Filter]:
        query = "SELECT * FROM filters WHERE id = ?"
        row = await self._fetch_one(query, (id,))
        if row is None:
            return None
        return Filter.model_validate(dict(row))
    
    async def get_by_name(self, name: str) -> Optional[Filter]:
        query = "SELECT * FROM filters WHERE name = ?"
        row = await self._fetch_one(query, (name,))
        if row is None:
            return None
        return Filter.model_validate(dict(row))
    
    async def list(self, **filters) -> list[Filter]:
        query = "SELECT * FROM filters"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if key == "name":
                    conditions.append("name LIKE ?")
                    params.append(f"%{value}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY name"
        
        rows = await self._fetch_all(query, tuple(params))
        return [Filter.model_validate(dict(row)) for row in rows]
    
    async def create(self, **data) -> Filter:
        import json
        if "excluded_tags" in data and data["excluded_tags"] is not None:
            data["excluded_tags"] = json.dumps(data["excluded_tags"])
        
        cols = ", ".join(data.keys())
        vals = ", ".join(["?" for _ in data])
        placeholders = tuple(data.values())
        query = f"INSERT INTO filters ({cols}) VALUES ({vals})"
        await self._execute(query, placeholders)
        
        created_id = await self._fetch_one("SELECT last_insert_rowid()")
        return await self.get(created_id[0])
    
    async def update(self, id: int, **data) -> Filter:
        import json
        if "excluded_tags" in data and data["excluded_tags"] is not None:
            data["excluded_tags"] = json.dumps(data["excluded_tags"])
        
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        params = tuple(data.values()) + (id,)
        query = f"UPDATE filters SET {set_clause} WHERE id = ?"
        await self._execute(query, params)
        return await self.get(id)
    
    async def delete(self, id: int) -> None:
        query = "DELETE FROM filters WHERE id = ?"
        await self._execute(query, (id,))
    
    async def exists(self, **filters) -> bool:
        query = "SELECT 1 FROM filters WHERE 1=1"
        params = []
        for key, value in filters.items():
            query += f" AND {key} = ?"
            params.append(value)
        row = await self._fetch_one(query, tuple(params))
        return row is not None