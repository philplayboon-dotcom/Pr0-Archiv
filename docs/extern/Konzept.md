# Konzept.md – Neustart der Entwicklung

> **Zweck:** Dieses Dokument beschreibt *Was* gebaut wird und *Warum*. Es dient als Entscheidungsgrundlage und Referenz für alle Beteiligten. Keine Architektur-Details (siehe `ARCHITECTURE.md`).

---

## 1. Projektzweck

**Pr0-Archiv** ist ein lokaler Desktop-Client (Windows, später Android) zum Archivieren von Inhalten von **pr0gramm.com**.

**Kernproblem:** Nutzer wollen Inhalte von pr0gramm.com dauerhaft lokal speichern, durchsuchbar machen, bewerten und in eigene Sammlungen organisieren – ohne auf die Online-Plattform angewiesen zu sein.

**Lösung:** Eine Flet-basierte App, die über die öffentliche API von pr0gramm.com Posts abruft (mit Cookie-Auth für NSFW/NSFL), Thumbnails lokal cachiert, Metadaten in SQLite persistiert und eine Offline-fähige Browse-/Sammlungs-/Datenbank-Oberfläche bietet.

---

## 2. Zielgruppen & Use Cases

| Zielgruppe | Primäre Use Cases |
|------------|-------------------|
| **Archivierer** | Einmaliger Vollscan (letzte 1.000 Posts), regelmäßige inkrementelle Updates, nachträgliches Backfill älterer Inhalte |
| **Browser** | Chronologisch durch Scrollen ältere Posts ansehen, Thumbnails an/aus, Filter nach Tags/Kategorien |
| **Kuratoren** | Posts mit 1–5 Sternen bewerten, eigene Tags hinzufügen, in thematische Sammlungen einsortieren |
| **Analysten** | Volltext-Suche über alle Metadaten, Filter nach Sammlung/Rating/Tags, Export (CSV/JSON/Excel) |
| **Multi-Account-Nutzer** | Bis zu 5 Accounts verwalten, schnelles Umschalten, Cookies sicher speichern |

---

## 3. Funktionale Anforderungen (Features)

### 3.1 Authentifizierung & Multi-Account (Prio: Kritisch)
- **Login-Flow:** Sichtbares Chromium-Fenster (Playwright) öffnet `pr0gramm.com/login` → User löst CAPTCHA manuell → App wartet auf `pp`-Cookie (Polling, max 5 Min) → Validierung via `GET /api/user/sync`
- **Account-Dropdown:** Zeigt bis zu 5 zuletzt genutzte Accounts (Username + "Letzter Login") → Auswahl → "Anmelden" (nutzt gespeicherten Cookie) oder "Neues Profil anmelden"
- **Cookie-Speicherung:** Nur validierte Cookies in DB (`accounts` Tabelle: username, cookie_hash, last_login, is_active) – Passwörter **niemals** speichern
- **Auto-Login:** Bei App-Start: Gültiger Cookie → direkt HomeView; Ungültig/Fehlend → LoginView

### 3.2 Scan / Inhalts-Abruf (Prio: Kritisch)
**Drei Scan-Modi:**
| Modus | Start | Richtung | Typischer Einsatz |
|-------|-------|----------|-------------------|
| **Initial** | `older=0` (neueste) | Vorwärts (neu → alt) | Ersteinrichtung, Default 1.000 Posts |
| **Incremental** | Letzter `completed` Scan (`oldest_pr0_id`) | Vorwärts | Regelmäßige Updates |
| **Backfill** | `MIN(pr0_id)` aus DB oder User-Start-ID | Rückwärts (alt → älter) | Nachträgliches Archivieren |

**Scan-Konfiguration (Input):**
- Modus (Initial/Incremental/Backfill)
- Flags: SFW(1) | NSFW(2) | NSFL(4) – bitweise kombinierbar (Default: 7 = alle)
- Max. Alter in Stunden (optional)
- Ausschluss-Tags (Client-seitig: Items mit einem der Tags werden **nicht** gespeichert)
- Ziel-Anzahl (500 | 1.000 | 5.000 | custom)
- Optional: Stopp bei bestimmter `pr0_id`
- Optional: Filter-ID (gespeicherter Filter aus DB)

**Scan-Ausführung:**
- Rate-Limit: 1–2 Sek Pause zwischen API-Calls
- HTTP 429 → Exponentielles Backoff (1s, 2s, 4s, 8s, max 30s, max 5 Retries)
- Thumbnails: max 5 parallel (Semaphore), Fehler → Item speichern **ohne** Thumbnail
- **scan_history** Tabelle: Jeder Scan wird protokolliert (Type, Status, Counts, Cursor, Config-Snapshot, Dauer)
- Abbruch: Cursor **nicht** aktualisieren → Wiederaufnahme möglich

**Filter-System:**
- Filter in DB: Name (UNIQUE), excluded_tags (JSON Array)
- Anwendung: Client-seitig während Scan – Item hat **einen** Tag aus excluded_tags → nicht speichern
- UI: Dropdown in Scan-Dialog + "Filter erstellen" Modal (Name + Tags comma-separated)

**Review-Queue (sofort nach erstem Item):**
- Medien: Image/GIF (BoxFit.CONTAIN), Video/Video+Audio (Flet `Video`), Fallback-Platzhalter
- Tags: Pr0-Tags (Read-only Chips) + User-Tags (Input comma-separated → Chips)
- Rating: 1–5 Sterne oder Dropdown
- Sammlungen: Dropdown (alle Collections) + "Neue Sammlung" Inline
- Navigation: [Zurück] [Überspringen] [Weiter & Speichern]
- Queue: `on_item_ready` Callback fügt Item hinzu → erstes Item **sofort** anzeigen

### 3.3 Browse / Durchsuchen (Prio: Hoch)
- **View:** `/browse` Route, **ListView** (nicht GridView!) – chronologisch, neueste zuerst
- **Navigation:** Erstes Item (neueste) angezeigt → "zurück gehend" = ältere Posts laden (Infinite Scroll / Pagination)
- **Media-Toggle:** Respektiert `show_thumbnails` Setting (aus → nur Metadaten)
- **Item-Card:** Thumbnail links, Metadaten rechts (per `ThumbnailCard` Control)

### 3.4 Sammlungen / Collections (Prio: Hoch)
- **CollectionsView (`/collections`):** Jede Sammlung = Button im Karten-Look (Spielkarte)
- **Karte:** Name zentriert, Hintergrundbild = Thumbnail des obersten Items der Sammlung
- **CRUD:** Erstellen, Umbenennen, Löschen, Drag&Drop-Reihenfolge (später)
- **Items in Sammlung:** Klick auf Karte → Grid/List der Items dieser Sammlung
- **Repository:** `add_item(collection_id, item_id)` nutzt `items.id` (PK), **nicht** `pr0_id`

### 3.5 Datenbank-Verwaltung (Prio: Mittel)
- **DatabaseView (`/database`):** Einfache Anzeige aller Items (DataTable oder ListView)
- **Spalten:** ID, Pr0-ID, Thumbnail, Typ, Tags, Rating, Gepostet, Gescannt, Sammlungen
- **Filter:** Suche (Volltext), Sammlung-Dropdown, Tags, Min-Rating
- **Pagination:** Vorherige/Nächste Seite
- **Bulk-Actions (später):** Tags hinzufügen, Rating setzen, Zu Sammlung, Löschen

### 3.6 Einstellungen (Prio: Mittel)
| Sektion | Felder |
|---------|--------|
| **Profile** | Liste aller Accounts (aus `accounts` Tabelle) mit "Löschen"-Button |
| **Datenbank** | Aktueller Pfad anzeigen + "Neue DB erstellen" + "DB laden" (FilePicker) |
| **Allgemein** | Thumbnails anzeigen (Switch), Scan-Limit, Auto-Scan-Intervall, Theme |
| **Login** | **ENTFERNEN** – Login gehört in `/login` View (nicht in Settings) |

### 3.7 Export / Import (Prio: Mittel)
- Export: CSV, JSON, Excel (alle relevanten Metadaten: pr0_id, URL, Datum, Tags, Rating, User-Tags, Sammlungen)
- Import: Bestehende Datenbestände einlesen (später)

---

## 4. Nicht-Funktionale Anforderungen

| Kategorie | Anforderung |
|-----------|-------------|
| **Plattform** | Windows Desktop (Flet 1.0.3), Android-Vorbereitung (StoragePaths, FilePicker, APK-Build) |
| **Performance** | UI bleibt während Scan/DB/Netzwerk reagierend (Async Only: `page.run_task`/`run_thread`), Thumbnails lazy laden, feste Größe 160×160 |
| **Datenschutz/Sicherheit** | Keine Passwörter/Secrets in Logs/Tests/Code; Cookie nur als `pp=value` im Header; SQLite WAL-Mode + `foreign_keys=ON` + `busy_timeout=5000` |
| **Offline-Fähigkeit** | Vollständig nutzbar nach erstem Scan (Thumbnails + Metadaten lokal) |
| **Responsive UI** | Desktop: NavigationRail links; <800px: NavigationBar unten (per `UI_GUIDELINES.md`) |
| **Design** | Obsidian-Red-Glass (schwarz-rot, teiltransparente Cards) per `UI_GUIDELINES.md` |
| **Testbarkeit** | MVVM: ViewModels ohne Flet-Imports testbar; `pytest tests/ -v`, `ruff check <datei> --fix` |
| **Wartbarkeit** | Clean Architecture: `core/` = Domain (keine Flet Imports), `presentation/` = UI; Repository-Protocols für DB-Abstraktion |

---

## 5. Technische Constraints & Rahmenbedingungen

| Constraint | Details |
|------------|---------|
| **Sprache** | Python 3.10+ (Syntax `int \| None`) |
| **UI Framework** | Flet **1.0.3** (Flutter 3.44.8) – `ft.run(main)`, `page.navigate()`, `ft.Button`/`ft.FilledButton`, `BoxFit.CONTAIN`, `ft.Video` |
| **Datenbank** | SQLite via `aiosqlite`, WAL-Mode, parametrisierte Queries |
| **Validierung** | Pydantic 2.x (`ConfigDict`, nicht class-based `Config`) |
| **HTTP** | `aiohttp` für pr0 API (Cookie-Header) |
| **Thumbnails** | `Pillow` für Konvertierung → JPEG 160×160, Quality 85 |
| **Export** | `pandas` + `openpyxl` für CSV/JSON/Excel |
| **Login-Automation** | `playwright>=1.63.0` (async, Chromium headless=False) |
| **Build** | `flet build apk` / `flet pack` (PyInstaller) |
| **Lint/Format** | `ruff` (ohne Projekt-Konfig, gezielt auf geänderte Dateien anwenden) |

---

## 6. Datenmodell (Kernentitäten)

| Entität | Schlüsselattribute |
|---------|-------------------|
| **Item** | `id` (PK), `pr0_id` (UNIQUE Business Key), `post_url`, `post_datetime`, `scan_datetime`, `thumbnail_path`, `content_type` (video/video_audio/image/gif), `content_path`, `pr0_tags` (JSON), `user_rating` (1–5), `user_tags` (JSON), `user_last_rated_at` |
| **Collection** | `id` (PK), `name` (UNIQUE), `description`, `color`, `created_at` |
| **ItemCollection** | `item_id` (FK→items.id), `collection_id` (FK→collections.id), PK(item_id, collection_id) |
| **ScanHistory** | `id`, `scan_type` (initial/incremental/backfill), `status` (running/completed/failed), `started_at`, `completed_at`, `oldest_pr0_id`, `newest_pr0_id`, `fetched_count`, `new_count`, `duplicate_count`, `error_message`, `config_snapshot` (JSON) |
| **Filter** | `id`, `name` (UNIQUE), `excluded_tags` (JSON Array), `created_at`, `updated_at` |
| **Account** | `id`, `username`, `display_name`, `cookie_hash`, `last_login`, `is_active`, `created_at` |
| **Settings** | `key` (PK), `value` (z. B. `show_thumbnails`, `scan_limit`, `theme`) |

**Wichtig:** `items.id` (PK) ≠ `items.pr0_id` (Business Key). Collection-Verknüpfung nutzt **`items.id`**.

---

## 7. Akzeptanzkriterien (Definition of Done)

- [ ] App startet ohne Fehler, zeigt LoginView bei fehlendem/ungültigem Cookie
- [ ] Login via Chromium: CAPTCHA manuell lösbar, `pp`-Cookie wird erkannt & validiert
- [ ] Account-Dropdown zeigt max 5 Accounts, sortiert nach `last_login` DESC
- [ ] Scan startet in allen 3 Modi, schreibt in `scan_history`, respektiert Rate-Limits
- [ ] Dedupe funktioniert: `pr0_id` UNIQUE → keine Duplikate in DB
- [ ] Thumbnails werden parallel (max 5) geladen, Fehler brechen Scan nicht ab
- [ ] Review-Queue zeigt erstes Item **sofort**, Navigation (Zurück/Überspringen/Weiter) funktional
- [ ] BrowseView: ListView chronologisch, Infinite Scroll, Media-Toggle wirkt
- [ ] Collections: CRUD + Items anzeigen, `add_item` nutzt `items.id`
- [ ] DatabaseView: Suche, Filter, Pagination funktional
- [ ] Settings: Profile verwalten, DB-Pfad wechseln, Thumbnails Toggle, Export
- [ ] Kein `page.go()`, keine blockierenden I/O im UI-Thread, `ruff check` auf geänderten Dateien grün

---

## 8. Auslieferungs-Phasen (nach `START-UPDATE.md` §9)

| Phase | Fokus | Haupt-Artefakte |
|-------|-------|-----------------|
| **1** | Database & Migrationen | Schema v3 (`scan_history`, `filters`, `accounts`), Repos, Bugfix `upsert()` (User-Daten erhalten), Collection-Bug Fix (`items.id` vs `pr0_id`) |
| **2** | Login & Auth | `LoginViewModel`, `LoginView` (Account-Dropdown, Chromium-Flow), `AuthService`, Routing Guard `/login` → `/` |
| **3a** | Scanner Service (Backend) | `ScanConfig`, `ScanHistory`, `Filter` Models, `ScanService.start_scan()` mit 3 Modi, `scan_history` CRUD, Rate-Limits, Filter-Anwendung |
| **3b** | Scanner UI (Frontend) | `ScanView` (3-Modi-Dialog, Filter-Dropdown/Editor), `ReviewView` + `ReviewViewModel` (Medien, Rating, Tags, Collections) |
| **4** | Integration & Polish | HomeView Redesign, BrowseView ListView, CollectionsView Karten, SettingsView Cleanup, E2E-Tests |

---

## 9. Abhängigkeiten & Externe Referenzen

| Thema | Referenz |
|-------|----------|
| Flet 1.0.3 API | `docs/extern/flet-api-1.0.3/` (gezielt suchen, nicht komplett lesen) |
| Flet Kompakt-Doku | `docs/extern/flet-kompakt.md` |
| pr0gramm API | `docs/API.md`, `docs/extern/pr0gramm-api.md` |
| UI Design Rules | `docs/UI_GUIDELINES.md` |
| Architektur-Entscheidungen | `docs/ARCHITECTURE.md`, `docs/decisions/` |
| Datenbank-Schema & Migrationen | `docs/DATABASE.md`, `docs/MIGRATIONS.md` |
| Scan-Pipeline Details | `docs/SCAN_PIPELINE.md` |
| Auth-Flow Details | `docs/AUTHENTICATION.md` |
| Error Handling | `docs/ERROR_HANDLING.md` |
| Bekannte Bugs | `docs/BUGS.md` |
| Requirements (Must/Could/Won't) | `docs/REQUIREMENTS.md` |

---

## 10. Offene Entscheidungen / Risiken

| Thema | Status | Hinweis |
|-------|--------|---------|
| **Android-Build Test** | Offen | Nach Phase 3 testen (`flet build apk`), JDK 17 + Android SDK nötig |
| **Sync-Implementation** | Später | Interface definiert (`sync_service.py`), Implementation (Supabase/Custom) später |
| **Multi-Select / Bulk-Actions** | Nice-to-have | Long-Press → Bulk-Actions in Browse/Database |
| **Performance >10k Items** | Später | Pagination/Indizes prüfen, Virtualisierung optimieren |
| **pr0 API Änderungen** | Laufend | Unversionierte API → robuste Fehlerbehandlung, Antworten nie ungeprüft annehmen |

---

## 11. Nächste Schritte (Sofort)

1. **Phase 1 starten:** `AGENTS_DATABASE` – Migration v3 ausführen, neue Repos implementieren, Bugfixes (`upsert` User-Daten erhalten, Collection-Bug `items.id` vs `pr0_id`) + Tests
2. **Parallel:** `requirements.txt` prüfen (`playwright>=1.63.0` für Login, `pandas`/`openpyxl` für Export)
3. **Chromium installieren:** `python -m playwright install chromium` (einmalig für Login-Flow)

---

*Erstellt: 2026-10-03*  
*Basiert auf: `START-UPDATE.md`, `REQUIREMENTS.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `FEATURES.md`, `BUGS.md`, `UI_GUIDELINES.md`, `AUTHENTICATION.md`, `AGENTS.md`*