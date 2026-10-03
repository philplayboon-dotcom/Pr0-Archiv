# ARCHITECTURE.md — Pr0-Archiv Technische Architektur

> Dokumentiert die architektonischen Entscheidungen für Phase 1 (Database & Migrationen).
> Basiert auf: [Konzept.md](../Konzept.md), Clean Architecture, Pydantic 2.x, aiosqlite.

---

## 1. Architektonischer Stil

### Clean Architecture (Layered)

```
┌─────────────────────────────────────────────────────────────┐
│                    presentation/                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Views     │  │ ViewModels  │  │   Flet Controls     │  │
│  │  (Phase 2+) │  │ (Phase 2+)  │  │   (Phase 4)         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ Dependency Injection
┌─────────────────────────────────────────────────────────────┐
│                        core/                                  │
│  ┌──────────┐ ┌────────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ Models   │ │ Repositories│ │ Database │ │  Services    │  │
│  │ (Domain) │ │ (Protocols) │ │ (Infra)  │ │ (Phase 2+)   │  │
│  └──────────┘ └────────────┘ └──────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Regel**: `core/` hat **keine Flet-Imports**. ViewModels sind testbar ohne UI-Framework.

---

## 2. Domain Models (Pydantic 2.x)

### Design-Entscheidungen

| Entscheidung | Begründung |
|-------------|------------|
| `ConfigDict(extra="forbid")` | Strenge Validierung, keine unbekannten Felder |
| `populate_by_name=True` | Aliases (`pr0_id`) funktionieren mit `model_dump(by_alias=True)` |
| JSON-Strings in DB | SQLite hat kein natives JSON-Typ, manuelle Serialisierung |
| `user_rating: int \| None` mit `ge=1, le=5` | Domain-Constraint auf Model-Ebene |

### Entity Relationship

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│   Item      │       │ ItemCollection   │       │ Collection  │
├─────────────┤       ├──────────────────┤       ├─────────────┤
│ id (PK)     │◄──────│ item_id (FK)     │       │ id (PK)     │
│ pr0_id (UK) │       │ collection_id(FK)│──────►│ name (UK)   │
│ ...         │       │ PK(item_id,      │       │ ...         │
└─────────────┘       │  collection_id)  │       └─────────────┘
                      └──────────────────┘
```

> **KRITISCH**: `ItemCollection.item_id` referenziert `Item.id` (PK), **NICHT** `Item.pr0_id` (Business Key).
> Dies ermöglicht Deduplikation: 2 Items mit gleichem `pr0_id` aber verschiedenen PKs können beide in Sammlungen existieren.

---

## 3. Repository Pattern

### Protocol-First Design

```python
# Protocol definiert Interface (testbar, austauschbar)
class ItemRepositoryProtocol(Protocol[Item]):
    async def get(self, id: int) -> Optional[Item]: ...
    async def get_by_pr0_id(self, pr0_id: int) -> Optional[Item]: ...
    async def upsert(self, pr0_id: int, **data) -> Item: ...  # Preserves user data!

# Implementation nutzt aiosqlite
class ItemRepository(BaseRepository[Item], ItemRepositoryProtocol):
    ...
```

### BaseRepository Utilities

```python
class BaseRepository(Generic[M]):
    def __init__(self, db):  # Accepts wrapper OR raw aiosqlite.Connection
        self.db = db
    
    async def _fetch_one(self, query, params=()):
        if hasattr(self.db, 'fetchone'):  # Wrapper
            return await self.db.fetchone(query, params)
        cursor = await self.db.execute(query, params)  # Raw connection
        return await cursor.fetchone()
```

---

## 4. Database Layer

### Connection Management

```python
class DatabaseConnection:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row  # WICHTIG für dict(row)
        # Pragmas pro Konzept.md
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute("PRAGMA foreign_keys=ON")
        await self._conn.execute("PRAGMA busy_timeout=5000")
        await self._conn.execute("PRAGMA synchronous=NORMAL")
        return self
```

### Migration System

```
v1_initial      → items Tabelle
v2_add_users    → collections, accounts, settings, item_collection
v3_schema       → ALLE 7 Tabellen + Indizes + _migrations + Pragmas
```

**Migration Tracking**:
```sql
CREATE TABLE _migrations (
    version TEXT UNIQUE,
    applied_at TEXT DEFAULT (datetime('now'))
);
```

**Idempotenz**: `CREATE TABLE IF NOT EXISTS` + `INSERT OR IGNORE INTO _migrations`

---

## 5. Schema v3 — Vollständig

### Tabellen

| Tabelle | Primärschlüssel | Foreign Keys | Indizes |
|---------|----------------|--------------|---------|
| `items` | `id` (AUTOINC) | — | `idx_items_pr0_id` |
| `collections` | `id` (AUTOINC) | — | — |
| `item_collection` | `(item_id, collection_id)` | `item_id→items.id`, `collection_id→collections.id` | `idx_item_collection_collection` |
| `scan_history` | `id` (AUTOINC) | — | `idx_scan_history_status` |
| `filters` | `id` (AUTOINC) | — | `idx_filters_name` |
| `accounts` | `id` (AUTOINC) | — | `idx_accounts_username` |
| `settings` | `key` | — | — |
| `_migrations` | `id` (AUTOINC) | — | — |

### Pragmas (Connection-Level)

```sql
PRAGMA journal_mode=WAL;           -- Bessere Concurrency
PRAGMA foreign_keys=ON;            -- FK Enforcement
PRAGMA busy_timeout=5000;          -- 5s Wait bei Lock
PRAGMA synchronous=NORMAL;         -- Balance Safety/Performance
```

---

## 6. Dependency Injection

### Pattern: Async Context Manager + Generator

```python
# main.py / App Setup
async def get_database(db_path: str = "pr0archiv.db") -> DatabaseConnection:
    async with DatabaseConnection(db_path) as db:
        yield db

# Usage in Services/ViewModels
class ItemService:
    def __init__(self, item_repo: ItemRepositoryProtocol):
        self.item_repo = item_repo
    
    async def sync_item(self, api_item: dict) -> Item:
        return await self.item_repo.upsert(**api_item)
```

### Repository Injection

```python
# In ViewModel (Phase 2+)
class BrowseViewModel:
    def __init__(self, item_repo: ItemRepositoryProtocol):
        self.item_repo = item_repo
    
    async def load_items(self, limit=50):
        self.items = await self.item_repo.get_recent(limit)
```

---

## 7. Security Considerations (Phase 1)

| Aspekt | Implementation |
|--------|----------------|
| Passwörter | **Nie gespeichert** — nur Cookie-Hash |
| Cookie-Storage | `accounts.cookie_hash` (SHA256 vom `pp=` Cookie) |
| SQL Injection | Parametrisierte Queries überall (`?` Platzhalter) |
| DB-Pragmas | `foreign_keys=ON`, `busy_timeout=5000` |
| WAL Mode | Ermöglicht gleichzeitige Reads während Write |

---

## 8. Performance Baseline (Phase 1)

| Operation | Erwartung | Messung |
|-----------|-----------|---------|
| Item Insert (Single) | < 5ms | — |
| Item Bulk Insert (1000) | < 500ms | — |
| Item Lookup by pr0_id | < 1ms (Index) | — |
| Collection Add Item | < 2ms | — |
| Scan History Write | < 3ms | — |

> Detaillierte Benchmarks in Phase 3 durch `PERFORMANCE_OPTIMIZER`.

---

## 9. Offene Architekturfragen

| Thema | Status | Hinweis |
|-------|--------|---------|
| Sync Service Interface | Definiert | Implementation später (Supabase/Custom) |
| Android Storage Paths | Offen | `flet.build.apk` testen nach Phase 3 |
| >10k Items Performance | Später | Pagination/Indizes prüfen |
| pr0 API Changes | Laufend | Robuste Fehlerbehandlung, Responses nie ungeprüft |

---

## 10. Referenzen

- [Konzept.md](../Konzept.md) — Requirements & Acceptance Criteria
- [Design.md](../design/Design.md) — Obsidian Red Glass UI System
- [AGENTS.md](../agents/AGENTS.md) — Agent Workflow
- [PHASE1_PROGRESS.md](../phase_docs/PHASE1_PROGRESS.md) — Aktueller Status

---

*Architektur-Version: 1.0 (Phase 1)*  
*Letzte Aktualisierung: 2026-10-03*  
*Entscheider: CODE_ARCHITECT + Supervisor*