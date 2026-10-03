from __future__ import annotations

from typing import Optional, List
from core.models import Item
from core.repositories.base import RepositoryProtocol, BaseRepository


class ItemRepositoryProtocol(RepositoryProtocol[Item]):
    """Protocol defining Item repository interface."""
    
    async def get_by_pr0_id(self, pr0_id: int) -> Optional[Item]: ...
    async def get_recent(self, limit: int = 50) -> List[Item]: ...
    async def get_by_tags(self, tags: list[str], limit: int = 100) -> List[Item]: ...
    async def count_all(self) -> int: ...
    async def bulk_create(self, items: list[dict]) -> list[Item]: ...
    async def upsert(self, pr0_id: int, **data) -> Item: ...


class ItemRepository(BaseRepository[Item], ItemRepositoryProtocol):
    """aiosqlite implementation of Item repository."""
    
    async def get(self, id: int) -> Optional[Item]:
        query = "SELECT * FROM items WHERE id = ?"
        row = await self._fetch_one(query, (id,))
        if row is None:
            return None
        return Item.model_validate(dict(row))
    
    async def get_by_pr0_id(self, pr0_id: int) -> Optional[Item]:
        query = "SELECT * FROM items WHERE pr0_id = ?"
        row = await self._fetch_one(query, (pr0_id,))
        if row is None:
            return None
        return Item.model_validate(dict(row))
    
    async def list(self, **filters) -> list[Item]:
        query = "SELECT * FROM items"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if key == "min_rating" and value is not None:
                    conditions.append("user_rating >= ?")
                    params.append(value)
                elif key == "max_rating" and value is not None:
                    conditions.append("user_rating <= ?")
                    params.append(value)
                elif key == "collection_id" and value is not None:
                    query = """
                        SELECT i.* FROM items i
                        JOIN item_collection ic ON i.id = ic.item_id
                        WHERE ic.collection_id = ?
                    """
                    params.append(value)
                    conditions = []  # Override
                    break
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC"
        
        if "limit" in filters and filters["limit"]:
            query += " LIMIT ?"
            params.append(filters["limit"])
        
        rows = await self._fetch_all(query, tuple(params))
        return [Item.model_validate(dict(row)) for row in rows]
    
    async def create(self, **data) -> Item:
        # Ensure JSON fields are properly serialized
        if "pr0_tags" in data and data["pr0_tags"] is not None:
            import json
            data["pr0_tags"] = json.dumps(data["pr0_tags"])
        if "user_tags" in data and data["user_tags"] is not None:
            import json
            data["user_tags"] = json.dumps(data["user_tags"])
        
        cols = ", ".join(data.keys())
        vals = ", ".join(["?" for _ in data])
        placeholders = tuple(data.values())
        query = f"INSERT INTO items ({cols}) VALUES ({vals})"
        await self._execute(query, placeholders)
        
        # Get the created item with its auto-generated ID
        created_id = await self._fetch_one("SELECT last_insert_rowid()")
        return await self.get(created_id[0])
    
    async def bulk_create(self, items: list[dict]) -> list[Item]:
        import json
        created = []
        for item_data in items:
            if "pr0_tags" in item_data and item_data["pr0_tags"] is not None:
                item_data["pr0_tags"] = json.dumps(item_data["pr0_tags"])
            if "user_tags" in item_data and item_data["user_tags"] is not None:
                item_data["user_tags"] = json.dumps(item_data["user_tags"])
            item = await self.create(**item_data)
            created.append(item)
        return created
    
    async def upsert(self, pr0_id: int, **data) -> Item:
        """Insert or update item by pr0_id (business key).
        
        CRITICAL BUGFIX: When updating, preserve user data (user_rating, user_tags, user_last_rated_at).
        """
        existing = await self.get_by_pr0_id(pr0_id)
        
        if existing:
            # Preserve user data if not explicitly provided
            if "user_rating" not in data:
                data["user_rating"] = existing.user_rating
            if "user_tags" not in data:
                data["user_tags"] = existing.user_tags
            if "user_last_rated_at" not in data:
                data["user_last_rated_at"] = existing.user_last_rated_at
            
            # Update existing
            import json
            if "pr0_tags" in data and data["pr0_tags"] is not None:
                data["pr0_tags"] = json.dumps(data["pr0_tags"])
            if "user_tags" in data and data["user_tags"] is not None:
                data["user_tags"] = json.dumps(data["user_tags"])
            
            set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
            params = tuple(data.values()) + (existing.id,)
            query = f"UPDATE items SET {set_clause} WHERE id = ?"
            await self._execute(query, params)
            return await self.get(existing.id)
        else:
            # Create new
            return await self.create(pr0_id=pr0_id, **data)
    
    async def update(self, id: int, **data) -> Item:
        import json
        if "pr0_tags" in data and data["pr0_tags"] is not None:
            data["pr0_tags"] = json.dumps(data["pr0_tags"])
        if "user_tags" in data and data["user_tags"] is not None:
            data["user_tags"] = json.dumps(data["user_tags"])
        
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        params = tuple(data.values()) + (id,)
        query = f"UPDATE items SET {set_clause} WHERE id = ?"
        await self._execute(query, params)
        return await self.get(id)
    
    async def delete(self, id: int) -> None:
        query = "DELETE FROM items WHERE id = ?"
        await self._execute(query, (id,))
    
    async def exists(self, **filters) -> bool:
        query = "SELECT 1 FROM items WHERE 1=1"
        params = []
        for key, value in filters.items():
            query += f" AND {key} = ?"
            params.append(value)
        row = await self._fetch_one(query, tuple(params))
        return row is not None
    
    async def get_recent(self, limit: int = 50) -> List[Item]:
        query = "SELECT * FROM items ORDER BY created_at DESC LIMIT ?"
        rows = await self._fetch_all(query, (limit,))
        return [Item.model_validate(dict(row)) for row in rows]
    
    async def get_by_tags(self, tags: list[str], limit: int = 100) -> List[Item]:
        # Simple implementation - could be optimized with FTS
        placeholders = ", ".join(["?" for _ in tags])
        query = f"""
            SELECT * FROM items 
            WHERE pr0_tags IS NOT NULL
            AND (
                {" OR ".join([f"json_each.value = ?" for _ in tags])}
            )
            ORDER BY created_at DESC LIMIT ?
        """
        params = tags + [limit]
        rows = await self._fetch_all(query, tuple(params))
        return [Item.model_validate(dict(row)) for row in rows]
    
    async def count_all(self) -> int:
        row = await self._fetch_one("SELECT COUNT(*) FROM items")
        return row[0] if row else 0