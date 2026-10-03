from __future__ import annotations

from typing import Optional, List
from core.models import ItemCollection
from core.repositories.base import RepositoryProtocol, BaseRepository


class ItemCollectionRepositoryProtocol(RepositoryProtocol[ItemCollection]):
    """Protocol defining ItemCollection repository interface."""
    
    async def get_by_collection(self, collection_id: int) -> List[dict]: ...
    async def add(self, item_id: int, collection_id: int) -> ItemCollection: ...
    async def remove(self, item_id: int, collection_id: int) -> bool: ...


class ItemCollectionRepository(BaseRepository[ItemCollection], ItemCollectionRepositoryProtocol):
    """aiosqlite implementation of ItemCollection repository.
    
    CRITICAL BUGFIX: Uses items.id (PK) NOT pr0_id (Business Key) as foreign key.
    """
    
    async def get(self, id: int) -> Optional[ItemCollection]:
        # Composite PK - not directly queryable by single ID
        return None
    
    async def list(self, **filters) -> list[ItemCollection]:
        query = "SELECT * FROM item_collection"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if key == "item_id":
                    conditions.append("item_id = ?")
                    params.append(value)
                elif key == "collection_id":
                    conditions.append("collection_id = ?")
                    params.append(value)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        rows = await self._fetch_all(query, tuple(params))
        return [ItemCollection.model_validate(dict(row)) for row in rows]
    
    async def create(self, **data) -> ItemCollection:
        query = "INSERT INTO item_collection (item_id, collection_id) VALUES (?, ?)"
        await self._execute(query, (data["item_id"], data["collection_id"]))
        return ItemCollection(item_id=data["item_id"], collection_id=data["collection_id"])
    
    async def add(self, item_id: int, collection_id: int) -> ItemCollection:
        """Add item to collection.
        
        CRITICAL BUGFIX: item_id must be items.id (PK), NOT pr0_id (Business Key).
        """
        query = "INSERT OR IGNORE INTO item_collection (item_id, collection_id) VALUES (?, ?)"
        await self._execute(query, (item_id, collection_id))
        return ItemCollection(item_id=item_id, collection_id=collection_id)
    
    async def update(self, id: int, **data) -> ItemCollection:
        # Not typically used for junction table
        return None
    
    async def delete(self, id: int) -> None:
        # Not typically used for junction table
        pass
    
    async def exists(self, **filters) -> bool:
        query = "SELECT 1 FROM item_collection WHERE 1=1"
        params = []
        for key, value in filters.items():
            query += f" AND {key} = ?"
            params.append(value)
        row = await self._fetch_one(query, tuple(params))
        return row is not None
    
    async def get_by_collection(self, collection_id: int) -> List[dict]:
        """Get all item links for a collection."""
        query = "SELECT * FROM item_collection WHERE collection_id = ?"
        rows = await self._fetch_all(query, (collection_id,))
        return [dict(row) for row in rows]
    
    async def remove(self, item_id: int, collection_id: int) -> bool:
        query = "DELETE FROM item_collection WHERE item_id = ? AND collection_id = ?"
        await self._execute(query, (item_id, collection_id))
        return True