# Designkonzept: Pr0-Archiv – Obsidian Red Glass

Dieses Dokument beschreibt das visuelle und interaktive Design-Konzept für den **Pr0-Archiv** Desktop-Client. Es dient als direkter Handlungsleitfaden für die Implementierung der UI/UX-Agenten.

---

## 1. Design-Philosophie & Metapher

Das Konzept folgt dem Namen **"Obsidian Red Glass"**.

*   **Obsidian:** Die Basis ist ein tiefes, sattes Schwarz und sehr dunkle Graustufen. Es vermittelt Wertigkeit, Fokus und Professionalität, passend zu einem "Archiv".
*   **Glass:** Navigationselemente und Karten (Cards) nutzen dezente Transparenz-Effekte (Acrylic/Blur), um Tiefe zu erzeugen und den modernen Desktop-Charakter zu unterstreichen.
*   **Red:** Ein dezentes, dunkleres Rot wird **homöopathisch** als Akzentfarbe eingesetzt. Es dient *ausschließlich* zur Highlight-Setzung, Signalisierung von Aktivität oder für primäre Aktionsknöpfe.

**Grundsatz:** Content First. Die UI tritt in den Hintergrund, um die archivierten Medien (Bilder/Videos) wirken zu lassen.

---

## 2. Farbpalette (Flet/Flutter kompatibel)

Es dürfen *nur* diese Farben verwendet werden. Keine Verläufe, außer bei den Glas-Effekten.

| Element | Farbe (Hex) | Flet `ft.colors` Äquivalent | Beschreibung |
|:---|:---|:---|:---|
| **Background (Deep)** | `#121212` | `ft.colors.GREY_900` | Haupt-Hintergrund der App. |
| **Surface (Dark)** | `#1E1E1E` | `ft.colors.GREY_850` | Feste Container, Menüs, die sich vom Hintergrund abheben. |
| **Glass (Translucent)** | `rgba(30, 30, 30, 0.7)` | `ft.colors.with_opacity(0.7, ft.colors.GREY_850)` | Überlagernde Elemente mit Blur-Effekt. |
| **Accent (Pr0-Red)** | `#EE4D2D` | `ft.colors.RED_ACCENT_400` | *NUR* für aktive Zustände, primäre Buttons, Slider. |
| **Text (Primary)** | `#FFFFFF` | `ft.colors.WHITE` | Haupttext, Titel. |
| **Text (Secondary)** | `#B0B0B0` | `ft.colors.GREY_400` | Metadaten, Beschreibungen, deaktivierte Icons. |
| **Borders/Lines** | `#333333` | `ft.colors.GREY_700` | Dezente Trennlinien, Card-Ränder. |

---

## 3. Typografie

Konsequente Nutzung einer serifenlosen, modernen Schriftart, die auf allen Plattformen gut lesbar ist.

*   **Font Family:** `Roboto` (Standard in Flet/Flutter) oder `Inter` (falls eingebettet).
*   **Hierarchie:**
    *   **Headline Large:** white, bold, size 24 (z.B. View-Titel `/browse`).
    *   **Headline Medium:** white, 600, size 18 (z.B. Sammlungs-Namen).
    *   **Body Large:** grey_400, size 16 (z.B. Tag-Input).
    *   **Body Small/Secondary:** grey_400, size 12 (z.B. Zeitstempel, Pr0-IDs).

---

## 4. UI-Elemente & Controls (Flet Spezifisch)

Implementierungsvorgaben für Standard-Komponenten.

### 4.1 Buttons
*   **Primary (Text Button):** `ft.TextButton` mit `foreground_color=ft.colors.RED_ACCENT_400`. Genutzt für "Speichern", "Login", "Scan Starten".
*   **Secondary (Elevated):** `ft.ElevatedButton` mit `bgcolor=ft.colors.GREY_850`, `color=ft.colors.WHITE`, `elevation=0`. Genutzt für "Abbrechen", "Überspringen".
*   **Icon Buttons:** `ft.IconButton` mit `icon_color=ft.colors.GREY_400`, `selected_icon_color=ft.colors.RED_ACCENT_400`.

### 4.2 Eingabefelder
*   **Style:** `ft.TextField` mit `border_color=ft.colors.GREY_700`, `focused_border_color=ft.colors.RED_ACCENT_400`, `cursor_color=ft.colors.RED_ACCENT_400`.
*   **Chips (Tags):** `ft.Chip` mit `bgcolor=ft.colors.GREY_850`, `label_style=ft.TextStyle(color=ft.colors.WHITE)`. Ausgewählte Chips erhalten `bgcolor=ft.colors.RED_ACCENT_400`.

### 4.3 Navigations-Struktur (Responsive)
*   **Desktop (>800px):** `ft.NavigationRail`.
    *   `bgcolor=ft.colors.GREY_900`
    *   `selected_icon_content=ft.Icon(..., color=ft.colors.RED_ACCENT_400)`
    *   `unselected_icon_content=ft.Icon(..., color=ft.colors.GREY_400)`
*   **Mobil (<800px):** `ft.NavigationBar`. Gleiches Farbschema.

---

## 5. View-Spezifische Design-Konzepte

Anwendung der Regeln auf die Kern-Views (siehe `Konzept.md §3`).

### 5.1 HomeView (`/`) – Das Dashboard
*   **Layout:** Grid-Layout mit Translucent Glass Cards.
*   **Inhalt:**
    *   **Card 1:** Status des letzten Scans (aus `scan_history`). Kleiner "Scan Jetzt"-Button (Red Accent).
    *   **Card 2:** Quick-Stats (Anzahl Items, Sammlungen).
    *   **Card 3:** Account-Status (aktiver User).

### 5.2 LoginView (`/login`)
*   **Ästhetik:** Zentraler Focus, minimalistisch.
*   **Hintergrund:** Deep Black (`#121212`).
*   **Elemente:**
    *   Account-Dropdown: `ft.Dropdown` im dunklen Stil.
    *   Primärer Button: "Neues Profil anmelden" (Red Accent).

### 5.3 BrowseView (`/browse`)
*   **Layout:** Vertikale `ft.ListView`.
*   **Item-Card (ThumbnailCard Control):**
    *   `ft.Container` mit `bgcolor=ft.colors.GREY_850`, abgerundete Ecken (`border_radius=10`), dezenter Border (`#333333`).
    *   **Links:** Thumbnail (feste Breite 160, `BoxFit.CONTAIN`).
    *   **Rechts:** Metadaten (Titel white, Tags/Rating grey_400).

### 5.4 ReviewView (während/nach Scan)
*   **Ästhetik:** "Immersive Mode". Das Medium steht im Mittelpunkt.
*   **Layout:** Zweispaltig.
    *   **Links:** Medienplayer (Bilder `ft.Image`, Videos `ft.Video`) füllt die Höhe aus, schwarzer Hintergrund.
    *   **Rechts:** Kontroll-Panel (Glass-Effekt, schwebend über dem linken Rand). Enthält Rating (1-5 Sterne, Sterne werden bei Hover/Select rot), Tag-Input, Collections-Dropdown.

### 5.5 CollectionsView (`/collections`)
*   **Layout:** `ft.GridView`.
*   **Sammlungs-Karte:**
    *   Seitenverhältnis einer Spielkarte.
    *   Hintergrundbild: Thumbnail des neuesten Items, abgedunkelt mit `ft.LinearGradient(colors=[ft.colors.BLACK, ft.colors.TRANSPARENT])`.
    *   Text: Sammlungs-Name zentriert, weiss, fett.

---

## 6. Motion & Interaktion

*   **Hover-Effekte:** Interaktive Elemente (Cards in Browse/Collections, Icons) ändern ihre Hintergrundfarbe leicht von `ft.colors.GREY_850` zu `ft.colors.GREY_700` oder färben Icons dezent rot.
*   **Übergänge:** Nutzung von Flets Standard-Animationen für `ft.AnimatedContainer`, wo sinnvoll (z.B. beim Aufklappen von Details). Keine übertriebenen Animationen.

---

## 7. Zusammenfassung für Agenten

Implementiere die UI strikt nach diesen Vorgaben. Priorisiere die Einhaltung der Farbpalette vor funktionaler Komplexität in frühen Phasen. Der Look muss "Dark, Clean, Modern" sein. Nutze `ft.Colors.with_opacity` für die Transparenz-Effekte der Glass-Komponenten.