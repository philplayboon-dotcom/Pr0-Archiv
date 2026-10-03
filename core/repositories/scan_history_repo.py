from __future__ import annotations

from typing import Optional, List
from core.models import ScanHistory
from core.repositories.base import RepositoryProtocol, BaseRepository


class ScanHistoryRepositoryProtocol(RepositoryProtocol[ScanHistory]):
    """Protocol defining ScanHistory repository interface."""
    
    async def get_latest(self) -> Optional[ScanHistory]: ...
    async def get_by_type(self, scan_type: str) -> List[ScanHistory]: ...


class ScanHistoryRepository(BaseRepository[ScanHistory], ScanHistoryRepositoryProtocol):
    """aiosqlite implementation of ScanHistory repository."""
    
    async def get(self, id: int) -> Optional[ScanHistory]:
        query = "SELECT * FROM scan_history WHERE id = ?"
        row = await self._fetch_one(query, (id,))
        if row is None:
            return None
        return ScanHistory.model_validate(dict(row))
    
    async def list(self, **filters) -> list[ScanHistory]:
        query = "SELECT * FROM scan_history"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if key == "status":
                    conditions.append("status = ?")
                    params.append(value)
                elif key == "scan_type":
                    conditions.append("scan_type = ?")
                    params.append(value)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY started_at DESC"
        
        if "limit" in filters and filters["limit"]:
            query += " LIMIT ?"
            params.append(filters["limit"])
        
        rows = await self._fetch_all(query, tuple(params))
        return [ScanHistory.model_validate(dict(row)) for row in rows]
    
    async def create(self, **data) -> ScanHistory:
        import json
        if "config_snapshot" in data and data["config_snapshot"] is not None:
            data["config_snapshot"] = json.dumps(data["config_snapshot"])
        
        cols = ", ".join(data.keys())
        vals = ", ".join(["?" for _ in data])
        placeholders = tuple(data.values())
        query = f"INSERT INTO scan_history ({cols}) VALUES ({vals})"
        await self._execute(query, placeholders)
        
        created_id = await self._fetch_one("SELECT last_insert_rowid()")
        return await self.get(created_id[0])
    
    async def update(self, id: int, **data) -> ScanHistory:
        import json
        if "config_snapshot" in data and data["config_snapshot"] is not None:
            data["config_snapshot"] = json.dumps(data["config_snapshot"])
        
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        params = tuple(data.values()) + (id,)
        query = f"UPDATE scan_history SET {set_clause} WHERE id = ?"
        await self._execute(query, params)
        return await self.get(id)
    
    async def delete(self, id: int) -> None:
        query = "DELETE FROM scan_history WHERE id = ?"
        await self._execute(query, (id,))
    
    async def exists(self, **filters) -> bool:
        query = "SELECT 1 FROM scan_history WHERE 1=1"
        params = []
        for key, value in filters.items():
            query += f" AND {key} = ?"
            params.append(value)
        row = await self._fetch_one(query, tuple(params))
        return row is not None
    
    async def get_latest(self) -> Optional[ScanHistory]:
        query = "SELECT * FROM scan_history ORDER BY started_at DESC LIMIT 1"
        row = await self._fetch_one(query)
        if row is None:
            return None
        return ScanHistory.model_validate(dict(row))
    
    async def get_by_type(self, scan_type: str) -> List[ScanHistory]:
        query = "SELECT * FROM scan_history WHERE scan_type = ? ORDER BY started_at DESC"
        rows = await self._fetch_all(query, (scan_type,))
        return [ScanHistory.model_validate(dict(row)) for row in rows]