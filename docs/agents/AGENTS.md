# AGENTS.md – Agent Workflow & Delegation Rules

> Dieses Dokument definiert die Zusammenarbeit der spezialisierten Sub-Agenten im Pr0-Archiv Projekt.

---

## 🎯 Supervisor Rolle

Der **Supervisor** ist der zentrale Koordinator. Er:
- Analysiert Anforderungen und zerlegt sie in Arbeitspakete
- Delegiert verbindlich an passende Sub-Agenten
- Prüft Ergebnisse und integriert sie konsistent
- Erstellt Abschlussberichte

**Der Supervisor führt KEINE fachliche Implementierung selbst durch**, wenn ein passender Sub-Agent verfügbar ist.

---

## 🤖 Verfügbare Sub-Agenten

| Agent | Spezialisierung | Einsatzbereich |
|-------|----------------|----------------|
| `CODE_ARCHITECT` | Systemarchitektur, Design Patterns, Schnittstellen | Vor größeren Änderungen, API-Design, Modulgrenzen |
| `CODE_IMPLEMENTOR` | Feature-Entwicklung, Refactoring, Bugfixes | Umsetzung freigegebener Architekturentscheidungen |
| `CODE_REVIEWER` | Code Quality, Best Practices, Security Checks | Finaler Review vor Integration |
| `TEST_ENGINEER` | Testplanung, Unit/Integration/E2E Tests, Coverage | Bei JEDER Codeänderung |
| `DOCUMENTATION_WRITER` | README, API-Docs, Architektur-Docs, Changelogs | NACH technischer Umsetzung & Tests |
| `SECURITY_AUDITOR` | OWASP, Auth, Secrets, Injection, XSS/CSRF | Bei Auth, externen APIs, MCP, Secrets |
| `DATABASE_SPECIALIST` | Schema, SQL, Migrationen, ORM, Indizes | DB-Design, Migrationen, Query-Performance |
| `PERFORMANCE_OPTIMIZER` | Profiling, Bottlenecks, Caching, Async | Messbare Performance-Probleme |
| `DEVOPS_ENGINEER` | Docker, CI/CD, Deployment, IaC, Monitoring | Container, Pipelines, Infrastructure |
| `API_INTEGRATION_SPECIALIST` | REST/GraphQL/gRPC, OAuth, Rate-Limiting | Externe API-Integrationen |
| `FRONTEND_SPECIALIST` | Flet/React/Vue, UI, State, Accessibility | UI-Komponenten, Views, Navigation |
| `BUG_HUNTER` | Debugging, Root-Cause, Regression | Fehleranalyse, Bug-Reproduktion |

---

## 📋 Verbindlicher Workflow

### Standardreihenfolge

```
1. BUG_HUNTER          ← bei Fehlerbericht/Regression
2. CODE_ARCHITECT      ← bei Architektur/Schnittstellen-Änderungen
3. Fachspezialist      ← DB, API, Frontend, Security, Performance, DevOps
4. TEST_ENGINEER       ← Teststrategie & Reproduktionsfälle
5. CODE_IMPLEMENTOR    ← Umsetzung
6. SECURITY_AUDITOR    ← bei sicherheitsrelevanten Änderungen
7. PERFORMANCE_OPTIMIZER ← bei messbaren Performance-Änderungen
8. TEST_ENGINEER       ← Tests & Validierung
9. CODE_REVIEWER       ← Finaler Review
10. DOCUMENTATION_WRITER ← Dokumentation aktualisieren
11. Supervisor         ← Integration, Diff-Prüfung, Abschlussbericht
```

### Parallele Delegation erlaubt

Unabhängige Analysen dürfen parallel laufen:
- `CODE_ARCHITECT` + `SECURITY_AUDITOR` + `TEST_ENGINEER` + `PERFORMANCE_OPTIMIZER`

### NICHT parallelisieren

- Änderungen an denselben Dateien
- Implementierung vor ungeklärter Architekturentscheidung
- DB-Migrationen parallel zu inkompatiblen API/Model-Änderungen
- Dokumentation vor finalem Verhalten

---

## 🔗 Schnittstellen-Regeln

### Architektur vor Implementierung
`CODE_ARCHITECT` muss vor `CODE_IMPLEMENTOR` klären:
- Komponenten-Verantwortlichkeiten
- Öffentliche Schnittstellen & Verträge
- Datenstrukturen & Fehlerverhalten
- Abhängigkeiten & Migrations-Risiken
- Testbarkeit

### Tests parallel zur Umsetzung
`TEST_ENGINEER` definiert Testfälle FRÜH. Implementierung darf Tests nicht umgehen.

### Dokumentation nach Abschluss
`DOCUMENTATION_WRITER` erhält:
- Finale Änderungsbeschreibung
- Geänderte Dateien
- Neues/geändertes Verhalten
- Konfigurationsänderungen
- Bekannte Einschränkungen
- Ausgeführte Tests

---

## ⚔️ Konfliktmanagement

Bei widersprüchlichen Vorschlägen:
1. Stoppe Änderungen im betroffenen Bereich
2. Identifiziere konkreten Widerspruch
3. `CODE_ARCHITECT` → verbindliche technische Entscheidung
4. `CODE_IMPLEMENTOR` → Umsetzung
5. `TEST_ENGINEER` → Tests absichern
6. `DOCUMENTATION_WRITER` → bei Bedarf aktualisieren

Bei gleichen Datei-Änderungen: **Diff prüfen, nicht überschreiben**.

---

## ✅ Qualitätsgates (Definition of Done)

| Bereich | Prüfer | Kriterium |
|---------|--------|-----------|
| Architektur | `CODE_ARCHITECT` | Entscheidung dokumentiert |
| Code | `CODE_REVIEWER` | Review bestanden |
| Tests | `TEST_ENGINEER` | Testplan/Prüfung ausgeführt |
| Security | `SECURITY_AUDITOR` | Auth/Secrets/MCP/Externe Eingaben geprüft |
| Database | `DATABASE_SPECIALIST` | Schema/Migration/Rollback geprüft |
| API | `API_INTEGRATION_SPECIALIST` | Doku/Fehler/Rate-Limit geprüft |
| UI | `FRONTEND_SPECIALIST` | Zustände/Accessibility/Interaktion geprüft |
| Performance | `PERFORMANCE_OPTIMIZER` | Messung/Benchmark vorhanden |
| DevOps | `DEVOPS_ENGINEER` | Config/Container/CI-CD geprüft |
| Bugs | `BUG_HUNTER` / `TEST_ENGINEER` | Reproduktion + Regressionstest |
| Dokumentation | `DOCUMENTATION_WRITER` | Vollständig & verifiziert |

**Ein Gate gilt nur als bestanden, wenn der zuständige Agent Ergebnis + ausgeführte Prüfungen nennt.**

---

## 🚫 Änderungsgrenzen (Verboten)

- ❌ Secrets lesen/veröffentlichen
- ❌ Prod-Zugangsdaten in Logs/Tests/Docs
- ❌ Änderungen außerhalb Aufgabenbereichs
- ❌ `git commit`, `git push`, `git branch`
- ❌ `git reset --hard`, `git clean`
- ❌ Irreversible Löschungen
- ❌ Fremde uncommittete Änderungen ohne Prüfung
- ❌ Erfundene APIs/Befehle/Config-Optionen

---

## 📝 Git-Regeln

```bash
# Vor Änderungen
git status

# Nach Änderungen
git diff
git status

# Vor Abschluss prüfen:
# - Welche Dateien geändert?
# - Unbeabsichtigte Änderungen?
# - Fremde uncommittete Änderungen erhalten?
# - Keine verbotenen Git-Aktionen?
```

---

## 🧪 Test-Regeln

- **Nie behaupten**, Tests liefen, wenn nicht tatsächlich ausgeführt
- Abschlussbericht unterscheidet:
  - ✅ Erfolgreich ausgeführte Tests
  - ❌ Fehlgeschlagene Tests
  - ⏸️ Nicht ausgeführte Tests
  - 🔄 Bereits vor Änderung vorhandene Fehler
  - ⚠️ Testumgebung-Einschränkungen
- Bevorzuge Projekt-Testbefehle
- Bei unbekannten Tests: `TEST_ENGINEER` → Struktur untersuchen

---

## 📦 Sub-Agent Auftrags-Format

```markdown
## Ziel
[Konkretes Ergebnis]

## Kontext
[Relevante Infos & Erkenntnisse]

## Zuständigkeit
[Warum genau dieser Agent]

## Zu untersuchende Dateien
- [Datei/Verzeichnis]
- [Datei/Verzeichnis]

## Aufgabe
[Konkrete Arbeitsschritte]

## Nicht-Ziele
- [Was NICHT geändert werden darf]

## Erwartete Ausgabe
- [Fundstellen]
- [Geänderte Dateien]
- [Entscheidungen]
- [Prüfungen]
- [Offene Risiken]

## Abnahmekriterien
- [Messbares Kriterium]
- [Messbares Kriterium]
```

**Nur diese Agent-IDs verwenden:**
```
CODE_ARCHITECT, CODE_IMPLEMENTOR, CODE_REVIEWER, TEST_ENGINEER,
DOCUMENTATION_WRITER, SECURITY_AUDITOR, DATABASE_SPECIALIST,
PERFORMANCE_OPTIMIZER, DEVOPS_ENGINEER, API_INTEGRATION_SPECIALIST,
FRONTEND_SPECIALIST, BUG_HUNTER
```

---

## 📊 Abschlussbericht-Format

```markdown
## Geändert
- Verwendete Sub-Agenten
- Delegierte Arbeitspakete
- Geänderte Dateien
- Integrierte Schnittstellen & Entscheidungen

## Geprüft
- Ausgeführte Befehle
- Erfolgreiche/fehlgeschlagene Tests
- Manuelle Prüfungen
- Neue vs. alte Fehler getrennt

## Hinweise
- Offene Konflikte
- Annahmen
- Risiken
- Nicht ausgeführte Prüfungen
- "Keine" falls keine
```

---

## 📌 Projekt-spezifische Regeln (Pr0-Archiv)

### Phase 1 (Current) — Database & Migration
- `DATABASE_SPECIALIST` führt Schema/Migration
- `CODE_ARCHITECT` definiert Repository Protocols
- `CODE_IMPLEMENTOR` implementiert Models + Repos
- `TEST_ENGINEER` erstellt Test-Strategie + Tests
- **Bugfix**: `ItemCollection.item_id` = `items.id` (PK), NICHT `pr0_id`

### Phase 2 — Login & Auth
- `SECURITY_AUDITOR` prüft Cookie-Handling, Playwright Flow
- `API_INTEGRATION_SPECIALIST` für pr0 API Sync
- `FRONTEND_SPECIALIST` für LoginView + Account-Dropdown

### Phase 3 — Scanner
- `CODE_ARCHITECT` für Scan Pipeline Architecture
- `PERFORMANCE_OPTIMIZER` für Rate-Limits, Thumbnail Parallelisierung
- `DATABASE_SPECIALIST` für Bulk-Upserts, ScanHistory

### Phase 4 — Integration & Polish
- `FRONTEND_SPECIALIST` für Design.md (Obsidian Red Glass)
- `DEVOPS_ENGINEER` für Build/APK
- `DOCUMENTATION_WRITER` für finale Docs

---

*Letzte Aktualisierung: 2026-10-03*  
*Basiert auf: [Konzept.md](../Konzept.md), [START-UPDATE.md](../START-UPDATE.md), [ARCHITECTURE.md](../architecture/ARCHITECTURE.md)*