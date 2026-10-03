# Pr0-Archiv — Documentation Hub

> Zentrale Anlaufstelle für alle Projektdokumentation. Alle Pfade sind relativ zum Repository-Root.

---

## 📋 Kern-Dokumentation

| Dokument | Pfad | Beschreibung |
|----------|------|--------------|
| **Konzept** | [Konzept.md](./Konzept.md) | Requirements, Acceptance Criteria, Phasen-Plan |
| **Architektur** | [architecture/ARCHITECTURE.md](./architecture/ARCHITECTURE.md) | Technische Architektur, Clean Architecture, Schema v3 |
| **Design System** | [design/Design.md](./design/Design.md) | Obsidian Red Glass UI Guidelines |
| **Agent Workflow** | [agents/AGENTS.md](./agents/AGENTS.md) | Delegation Rules, Qualitätsgates, Git-Regeln |

---

## 📦 Phasen-Dokumentation

| Phase | Dokument | Status |
|-------|----------|--------|
| **Phase 1** | [phase_docs/PHASE1_PROGRESS.md](./phase_docs/PHASE1_PROGRESS.md) | 🟡 In Bearbeitung |
| **Phase 2** | *geplant* | ⏳ Login & Auth |
| **Phase 3a** | *geplant* | ⏳ Scanner Backend |
| **Phase 3b** | *geplant* | ⏳ Scanner UI |
| **Phase 4** | *geplant* | ⏳ Integration & Polish |

---

## 🔧 Technische Referenzen

| Referenz | Pfad |
|----------|------|
| pr0gramm API | [extern/pr0gramm-api.md](./extern/pr0gramm-api.md) |
| Flet 1.0.3 API | [extern/flet-api-1.0.3/](./extern/flet-api-1.0.3/) |
| UI Guidelines | [UI_GUIDELINES.md](./UI_GUIDELINES.md) |
| Database Schema | [DATABASE.md](./DATABASE.md) |
| Migrations | [MIGRATIONS.md](./MIGRATIONS.md) |
| Scan Pipeline | [SCAN_PIPELINE.md](./SCAN_PIPELINE.md) |
| Authentication | [AUTHENTICATION.md](./AUTHENTICATION.md) |
| Error Handling | [ERROR_HANDLING.md](./ERROR_HANDLING.md) |
| Known Bugs | [BUGS.md](./BUGS.md) |
| Requirements | [REQUIREMENTS.md](./REQUIREMENTS.md) |

---

## 🚀 Quickstart für Agenten

```bash
# 1. Konzept lesen (Was & Warum)
cat docs/Konzept.md

# 2. Architektur verstehen (Wie)
cat docs/architecture/ARCHITECTURE.md

# 3. Agent Rules beachten
cat docs/agents/AGENTS.md

# 4. Design System für UI-Arbeiten
cat docs/design/Design.md

# 5. Aktuellen Phasen-Status prüfen
cat docs/phase_docs/PHASE1_PROGRESS.md
```

---

## 📁 Ordnerstruktur

```
docs/
├── README.md                    # Dieser Hub
├── Konzept.md                   # Master Requirements
├── START-UPDATE.md              # Start-Prozedur & Updates
├── UI_GUIDELINES.md             # UI Design Rules
├── architecture/
│   └── ARCHITECTURE.md          # Technische Architektur
├── design/
│   └── Design.md                # Obsidian Red Glass
├── agents/
│   └── AGENTS.md                # Workflow & Delegation
├── phase_docs/
│   └── PHASE1_PROGRESS.md       # Phase 1 Detail-Status
└── extern/
    ├── pr0gramm-api.md
    ├── flet-api-1.0.3/
    └── flet-kompakt.md
```

---

## 🔄 Dokumentations-Workflows

### Für `DOCUMENTATION_WRITER`:
1. Neue Docs in passenden Unterordner ablegen
2. `docs/README.md` aktualisieren (Tabelle & Struktur)
3. Relative Pfade verwenden (keine absoluten)
4. Bei neuen Phasen: `phase_docs/PHASE{X}_PROGRESS.md` erstellen

### Für alle Agenten:
- **Lesen** aus `docs/` vor Beginn der Arbeit
- **Schreiben** Nachweise/Entscheidungen in `docs/phase_docs/`
- **Aktualisieren** `docs/README.md` bei strukturellen Änderungen

---

*Letzte Aktualisierung: 2026-10-03*  
*Maintainer: DOCUMENTATION_WRITER + Supervisor*