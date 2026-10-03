from __future__ import annotations

from typing import Optional, List
from core.models import Collection
from core.repositories.base import RepositoryProtocol, BaseRepository


class CollectionRepositoryProtocol(RepositoryProtocol[Collection]):
    """Protocol defining Collection repository interface."""
    
    async def get_by_name(self, name: str) -> Optional[Collection]: ...
    async def add_item(self, collection_id: int, item_id: int) -> bool: ...
    async def get_items_in_collection(self, collection_id: int) -> List[dict]: ...
    async def remove_item(self, collection_id: int, item_id: int) -> bool: ...


class CollectionRepository(BaseRepository[Collection], CollectionRepositoryProtocol):
    """aiosqlite implementation of Collection repository."""
    
    async def get(self, id: int) -> Optional[Collection]:
        query = "SELECT * FROM collections WHERE id = ?"
        row = await self._fetch_one(query, (id,))
        if row is None:
            return None
        return Collection.model_validate(dict(row))
    
    async def get_by_name(self, name: str) -> Optional[Collection]:
        query = "SELECT * FROM collections WHERE name = ?"
        row = await self._fetch_one(query, (name,))
        if row is None:
            return None
        return Collection.model_validate(dict(row))
    
    async def list(self, **filters) -> list[Collection]:
        query = "SELECT * FROM collections"
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
        return [Collection.model_validate(dict(row)) for row in rows]
    
    async def create(self, **data) -> Collection:
        cols = ", ".join(data.keys())
        vals = ", ".join(["?" for _ in data])
        placeholders = tuple(data.values())
        query = f"INSERT INTO collections ({cols}) VALUES ({vals})"
        await self._execute(query, placeholders)
        
        created_id = await self._fetch_one("SELECT last_insert_rowid()")
        return await self.get(created_id[0])
    
    async def update(self, id: int, **data) -> Collection:
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        params = tuple(data.values()) + (id,)
        query = f"UPDATE collections SET {set_clause} WHERE id = ?"
        await self._execute(query, params)
        return await self.get(id)
    
    async def delete(self, id: int) -> None:
        query = "DELETE FROM collections WHERE id = ?"
        await self._execute(query, (id,))
    
    async def exists(self, **filters) -> bool:
        query = "SELECT 1 FROM collections WHERE 1=1"
        params = []
        for key, value in filters.items():
            query += f" AND {key} = ?"
            params.append(value)
        row = await self._fetch_one(query, tuple(params))
        return row is not None
    
    async def add_item(self, collection_id: int, item_id: int) -> bool:
        """Add item to collection using items.id (PK), NOT pr0_id (Business Key).
        
        CRITICAL BUGFIX: This uses items.id (PK) as the foreign key.
        """
        query = "INSERT OR IGNORE INTO item_collection (item_id, collection_id) VALUES (?, ?)"
        await self._execute(query, (item_id, collection_id))
        return True
    
    async def get_items_in_collection(self, collection_id: int) -> List[dict]:
        """Get all item links for a collection."""
        query = "SELECT * FROM item_collection WHERE collection_id = ?"
        rows = await self._fetch_all(query, (collection_id,))
        return [dict(row) for row in rows]
    
    async def remove_item(self, collection_id: int, item_id: int) -> bool:
        query = "DELETE FROM item_collection WHERE collection_id = ? AND item_id = ?"
        await self._execute(query, (collection_id, item_id))
        return True