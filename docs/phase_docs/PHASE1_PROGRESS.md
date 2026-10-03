# Phase 1 Progress Report — Database & Migrationen

**Datum**: 2026-10-03  
**Status**: 🟡 In Bearbeitung (Implementation ✅, Tests 🟡)  
**Nächster Meilenstein**: Tests grün, dann Phase 2 Start

---

## ✅ Implementiert

### 1. Core Models (7 Pydantic 2.x Entitäten)
| Datei | Status | Beschreibung |
|-------|--------|--------------|
| `core/models/item.py` | ✅ | Item mit Validierung (rating 1-5, JSON Tags) |
| `core/models/collection.py` | ✅ | Collection mit UNIQUE name |
| `core/models/item_collection.py` | ✅ | Junction Table — **PK-Bugfix implementiert** |
| `core/models/scan_history.py` | ✅ | Scan-Protokoll mit config_snapshot |
| `core/models/filter.py` | ✅ | Filter mit excluded_tags (JSON) |
| `core/models/account.py` | ✅ | Account mit cookie_hash |
| `core/models/settings.py` | ✅ | Key-Value Settings |

### 2. Repository Layer (7 Repositories + Protocols)
| Repository | Protocol | Implementation | Status |
|------------|----------|----------------|--------|
| ItemRepository | ✅ | ✅ | CRUD, upsert (preserves user data), bulk |
| CollectionRepository | ✅ | ✅ | CRUD, add_item (uses PK!) |
| ItemCollectionRepository | ✅ | ✅ | CRUD, dedupe-safe |
| ScanHistoryRepository | ✅ | ✅ | CRUD, get_latest, get_by_type |
| FilterRepository | ✅ | ✅ | CRUD, get_by_name |
| AccountRepository | ✅ | ✅ | CRUD, get_active_accounts |
| SettingsRepository | ✅ | ✅ | get/set value, list |

### 3. Database Layer
| Komponente | Status | Beschreibung |
|------------|--------|--------------|
| `DatabaseConnection` | ✅ | Wrapper mit WAL, FK, busy_timeout |
| `MigrationManager` | ✅ | v1→v2→v3, _migrations tracking |
| `queries.py` | ✅ | Zentrale parametrisierte SQL |
| Schema v3 SQL | ✅ | 7 Tabellen + Indizes + Pragmas |

### 4. Main Entry Point
- `main.py`: Felt App mit NavigationRail (Desktop) + NavigationBar (Mobile <800px)
- DB-Initialisierung beim Start
- Responsive Layout

### 5. Test Infrastructure
- `pytest.ini`: asyncio_mode=strict konfiguriert
- `tests/conftest.py`: Async fixtures mit pytest-asyncio
- 70 Test Cases geschrieben

---

## 🟡 Offene Test-Issues (Priorität: Hoch)

### Migration Tests (6/6 failed)
```
Problem: Raw aiosqlite.Connection hat keine fetchone/fetchall Methoden
Lösung: Helper-Functions in conftest.py oder Wrapper nutzen
```

### Repository Integration Tests (30/42 failed)
```
1. Schema-Mismatch: Test-Schema fehlt user_tags, created_at, updated_at Spalten
2. JSON-Deserialisierung: excluded_tags, config_snapshot, pr0_tags als Strings in DB
3. Model Config: extra="forbid" lehnt DB-Spalten ab (created_at, updated_at)
4. Item.upsert: user_tags Spalte fehlt in Test-Schema
```

### Bugfix Verification Tests (2/2 failed)
```
Hängen an Repository Tests — werden mit Fix oben grün
```

---

## 🔧 Konkrete Fixes für Tests

### 1. Test-Schema erweitern (`tests/conftest.py` apply_schema_v3)
```sql
-- items Tabelle um fehlende Spalten ergänzen:
user_tags JSON NOT NULL DEFAULT '[]',
created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))

-- collections:
updated_at TEXT NOT NULL DEFAULT ...

-- filters:
updated_at TEXT NOT NULL DEFAULT ...

-- scan_history:
config_snapshot als JSON (bereits OK, aber Deserialisierung fixen)

-- settings:
updated_at TEXT NOT NULL DEFAULT ...
```

### 2. Repository JSON-Deserialisierung fixen
```python
# In allen Repositories get()/list() Methoden:
import json

# Bei Row-Objekten:
row_dict = dict(row)
if 'excluded_tags' in row_dict and isinstance(row_dict['excluded_tags'], str):
    row_dict['excluded_tags'] = json.loads(row_dict['excluded_tags'])
if 'config_snapshot' in row_dict and isinstance(row_dict['config_snapshot'], str):
    row_dict['config_snapshot'] = json.loads(row_dict['config_snapshot'])
if 'pr0_tags' in row_dict and isinstance(row_dict['pr0_tags'], str):
    row_dict['pr0_tags'] = json.loads(row_dict['pr0_tags'])
if 'user_tags' in row_dict and isinstance(row_dict['user_tags'], str):
    row_dict['user_tags'] = json.loads(row_dict['user_tags'])
```

### 3. Model Config anpassen
```python
# Option A: extra="ignore" (einfacher)
model_config = ConfigDict(extra="ignore", populate_by_name=True)

# Option B: created_at/updated_at Felder zu Models hinzufügen (sauberer)
```

### 4. Migration Test Helpers
```python
# In conftest.py für Raw-Connection:
async def fetchone(conn, query, params=()):
    cursor = await conn.execute(query, params)
    return await cursor.fetchone()

async def fetchall(conn, query, params=()):
    cursor = await conn.execute(query, params)
    return await cursor.fetchall()
```

---

## 📊 Code Quality

```bash
# Linting
ruff check . --fix
# Erwartet: 0 Errors nach Fixes

# Type Checking (optional)
# mypy core/ --strict
```

---

## 🎯 Definition of Done für Phase 1

- [ ] `pytest tests/ -v` → **70/70 passed**
- [ ] `ruff check . --fix` → **0 Errors**
- [ ] `python main.py` → **Startet ohne Fehler**
- [ ] Bugfix verifiziert: `ItemCollection.item_id` = `items.id` (PK)
- [ ] Schema v3 vollständig: 7 Tabellen + Indizes + _migrations

---

## 📦 Nächste Schritte (Phase 2)

Nach Phase 1 Abschluss:
1. **Phase 2 Start**: `CODE_ARCHITECT` → Auth Architecture
2. `SECURITY_AUDITOR` → Cookie/Playwright Security Review
3. `CODE_IMPLEMENTOR` → AuthService, LoginViewModel, LoginView
4. `FRONTEND_SPECIALIST` → Account-Dropdown, LoginView ([Design.md](../design/Design.md))
5. `TEST_ENGINEER` → Auth Flow Tests

---

## 📝 Lessons Learned (Phase 1)

1. **Async Fixtures**: pytest-asyncio 1.4+ erfordert `@pytest_asyncio.fixture` für async fixtures
2. **Row Factory**: `conn.row_factory = aiosqlite.Row` zwingend für dict(row)
3. **JSON in SQLite**: Immer manuell serialisieren/deserialisieren (kein Auto-JSON)
4. **Model Config**: `extra="forbid"` erfordert exakte Schema-Model-Übereinstimmung
5. **Test Isolation**: Jeder Test braucht frische DB (rollback oder recreate)

---

*Erstellt: 2026-10-03*  
*Supervisor: Pr0-Archiv Multi-Agent System*