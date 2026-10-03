from __future__ import annotations

from typing import Optional, List
from core.models import Account
from core.repositories.base import RepositoryProtocol, BaseRepository


class AccountRepositoryProtocol(RepositoryProtocol[Account]):
    """Protocol defining Account repository interface."""
    
    async def get_by_username(self, username: str) -> Optional[Account]: ...
    async def get_active_accounts(self, limit: int = 5) -> List[Account]: ...


class AccountRepository(BaseRepository[Account], AccountRepositoryProtocol):
    """aiosqlite implementation of Account repository."""
    
    async def get(self, id: int) -> Optional[Account]:
        query = "SELECT * FROM accounts WHERE id = ?"
        row = await self._fetch_one(query, (id,))
        if row is None:
            return None
        return Account.model_validate(dict(row))
    
    async def get_by_username(self, username: str) -> Optional[Account]:
        query = "SELECT * FROM accounts WHERE username = ?"
        row = await self._fetch_one(query, (username,))
        if row is None:
            return None
        return Account.model_validate(dict(row))
    
    async def list(self, **filters) -> list[Account]:
        query = "SELECT * FROM accounts"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if key == "is_active":
                    conditions.append("is_active = ?")
                    params.append(1 if value else 0)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY last_login DESC"
        
        if "limit" in filters and filters["limit"]:
            query += " LIMIT ?"
            params.append(filters["limit"])
        
        rows = await self._fetch_all(query, tuple(params))
        return [Account.model_validate(dict(row)) for row in rows]
    
    async def create(self, **data) -> Account:
        cols = ", ".join(data.keys())
        vals = ", ".join(["?" for _ in data])
        placeholders = tuple(data.values())
        query = f"INSERT INTO accounts ({cols}) VALUES ({vals})"
        await self._execute(query, placeholders)
        
        created_id = await self._fetch_one("SELECT last_insert_rowid()")
        return await self.get(created_id[0])
    
    async def update(self, id: int, **data) -> Account:
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        params = tuple(data.values()) + (id,)
        query = f"UPDATE accounts SET {set_clause} WHERE id = ?"
        await self._execute(query, params)
        return await self.get(id)
    
    async def delete(self, id: int) -> None:
        query = "DELETE FROM accounts WHERE id = ?"
        await self._execute(query, (id,))
    
    async def exists(self, **filters) -> bool:
        query = "SELECT 1 FROM accounts WHERE 1=1"
        params = []
        for key, value in filters.items():
            query += f" AND {key} = ?"
            params.append(value)
        row = await self._fetch_one(query, tuple(params))
        return row is not None
    
    async def get_active_accounts(self, limit: int = 5) -> List[Account]:
        query = "SELECT * FROM accounts WHERE is_active = 1 ORDER BY last_login DESC LIMIT ?"
        rows = await self._fetch_all(query, (limit,))
        return [Account.model_validate(dict(row)) for row in rows]