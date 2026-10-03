# Pr0-Archiv

Ein lokaler Desktop-Client (Windows, später Android) zum Archivieren von Inhalten von **pr0gramm.com**.

## 📋 Projektstatus

| Phase | Status | Fokus |
|-------|--------|-------|
| **Phase 1** | 🟡 In Bearbeitung | Database & Migrationen |
| **Phase 2** | ⏳ Geplant | Login & Auth |
| **Phase 3a** | ⏳ Geplant | Scanner Service (Backend) |
| **Phase 3b** | ⏳ Geplant | Scanner UI (Frontend) |
| **Phase 4** | ⏳ Geplant | Integration & Polish |

> **Aktuell**: Phase 1 - Database Schema, Repository Layer und Migrationen implementiert. Tests benötigen noch Schema/Model-Alignment.

## 🏗 Architektur

```
Pr0-Archiv/
├── main.py                    # Flet App Entry Point
├── requirements.txt           # Dependencies
├── pytest.ini                # Test Configuration
├── core/                      # Clean Architecture: Domain Layer
│   ├── models/               # Pydantic 2.x Models (7 Entitäten)
│   ├── repositories/         # Repository Protocols + Implementations
│   ├── database/             # Connection, Migrations, Queries
│   └── services/             # Business Logic (Phase 2+)
├── presentation/             # UI Layer (Flet)
│   ├── views/                # Flet Views (Phase 2+)
│   └── viewmodels/           # MVVM ViewModels (Phase 2+)
└── tests/                    # Test Suite
    ├── models/               # Unit Tests (28/28 ✅)
    ├── repositories/         # Integration Tests
    ├── migrations/           # Migration Tests
    └── test_bugfixes.py      # Critical Bugfix Verification
```

## 🗄 Datenmodell (Phase 1 - 7 Entitäten)

| Entität | Beschreibung | Schlüsselattribute |
|---------|-------------|-------------------|
| **Item** | pr0gramm Post | `id` (PK), `pr0_id` (UNIQUE), `user_rating` (1-5), Tags |
| **Collection** | Benutzer-Sammlung | `id` (PK), `name` (UNIQUE), `color` |
| **ItemCollection** | Junction Table | `item_id` (FK→items.id), `collection_id` |
| **ScanHistory** | Scan-Protokoll | `scan_type`, `status`, `config_snapshot` |
| **Filter** | Ausschluss-Filter | `name` (UNIQUE), `excluded_tags` (JSON) |
| **Account** | Benutzer-Account | `username`, `cookie_hash`, `is_active` |
| **Settings** | App-Einstellungen | `key` (PK), `value` |

> **Wichtig**: `ItemCollection` nutzt `items.id` (PK), **NICHT** `items.pr0_id` (Business Key) — expliziter Bugfix aus Konzept.md §6.

## 🛠 Technische Constraints

- **Python**: 3.10+ (Syntax `int \| None`)
- **UI Framework**: Flet 1.0.3 (Flutter 3.44.8)
- **Datenbank**: SQLite via `aiosqlite`, WAL-Mode, `foreign_keys=ON`, `busy_timeout=5000`
- **Validierung**: Pydantic 2.x (`ConfigDict`)
- **HTTP**: `aiohttp` für pr0 API
- **Thumbnails**: `Pillow` → JPEG 160×160, Quality 85
- **Export**: `pandas` + `openpyxl` für CSV/JSON/Excel
- **Login**: `playwright>=1.63.0` (Chromium headless=False)
- **Lint/Format**: `ruff`

## 🚀 Quickstart

```bash
# Dependencies installieren
pip install -r requirements.txt

# Playwright Chromium installieren (einmalig)
python -m playwright install chromium

# Tests ausführen
pytest tests/ -v

# Code Quality prüfen
ruff check . --fix

# App starten
python main.py
```

## 🧪 Test Status

```
✅ Model Unit Tests:        28/28 passed
🟡 Repository Integration:  12/42 passed (Schema/Model alignment needed)
🟡 Migration Tests:         0/6 passed (raw connection helpers needed)
✅ Bugfix Verification:     0/2 passed (depends on repo tests)
```

### Bekannte Test-Issues (Phase 1)
1. Test-Schema fehlt Spalten: `user_tags`, `created_at`, `updated_at`
2. JSON-Deserialisierung in Repositories (`excluded_tags`, `config_snapshot`, `pr0_tags`)
3. Model Config `extra="forbid"` lehnt DB-Spalten ab
4. Migration Tests nutzen Raw-Connection ohne Helper-Methoden

## 📚 Dokumentation (in `docs/`)

- [Konzept.md](./docs/Konzept.md) — Anforderungen & Acceptance Criteria
- [Design.md](./docs/design/Design.md) — Obsidian Red Glass UI Design System
- [AGENTS.md](./docs/agents/AGENTS.md) — Agent Workflow & Delegation Rules
- [ARCHITECTURE.md](./docs/architecture/ARCHITECTURE.md) — Technische Architektur (Phase 1)
- [Phase 1 Progress](./docs/phase_docs/PHASE1_PROGRESS.md) — Detaillierter Fortschritt & Offene Issues

## 🔗 Externe Referenzen

- [pr0gramm API](./docs/extern/pr0gramm-api.md)
- [Flet 1.0.3 API](./docs/extern/flet-api-1.0.3/)
- [UI Guidelines](./docs/UI_GUIDELINES.md)

## 📦 Build & Deploy

```bash
# Desktop (PyInstaller via Flet)
flet pack main.py

# Android APK
flet build apk
```

> **Hinweis**: Android-Build erfordert JDK 17 + Android SDK (nach Phase 3 testen)

## 🤝 Contributing

1. Phase 1 Tests grün bekommen (Schema/Model Alignment)
2. Phase 2: Login & Auth implementieren
3. Code Quality: `ruff check . --fix` muss grün sein
4. Tests für neue Features hinzufügen

## 📄 Lizenz

Internes Projekt — Pr0-Archiv Team