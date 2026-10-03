from __future__ import annotations

import flet as ft
from core.database import get_database, MigrationManager


async def main(page: ft.Page):
    """Main entry point for Pr0-Archiv Flet application."""
    page.title = "Pr0-Archiv"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    
    # Initialize database
    db = await get_database("pr0archiv.db")
    migration = MigrationManager(db)
    await migration.apply_migrations()

    # Navigation
    def on_nav_change(e):
        selected_index = e.control.selected_index
        routes = ["/", "/browse", "/collections", "/database", "/settings", "/login"]
        if 0 <= selected_index < len(routes):
            route = routes[selected_index]
            page.route = route
            page.update()
    
    # Navigation Rail (Desktop)
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        bgcolor="#1E1E1E",
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.HOME_OUTLINED, color="#B0B0B0"),
                selected_icon=ft.Icon(ft.Icons.HOME, color="#EE4D2D"),
                label="Home",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.BROWSE_GALLERY_OUTLINED, color="#B0B0B0"),
                selected_icon=ft.Icon(ft.Icons.BROWSE_GALLERY, color="#EE4D2D"),
                label="Browse",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.COLLECTIONS_OUTLINED, color="#B0B0B0"),
                selected_icon=ft.Icon(ft.Icons.COLLECTIONS, color="#EE4D2D"),
                label="Sammlungen",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.STORAGE_OUTLINED, color="#B0B0B0"),
                selected_icon=ft.Icon(ft.Icons.STORAGE, color="#EE4D2D"),
                label="Datenbank",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.SETTINGS_OUTLINED, color="#B0B0B0"),
                selected_icon=ft.Icon(ft.Icons.SETTINGS, color="#EE4D2D"),
                label="Einstellungen",
            ),
        ],
        on_change=on_nav_change,
    )
    
    # Navigation Bar (Mobile fallback)
    nav_bar = ft.NavigationBar(
        selected_index=0,
        bgcolor="#1E1E1E",
        indicator_color="#EE4D2D",
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icon(ft.Icons.HOME_OUTLINED, color="#B0B0B0"),
                selected_icon=ft.Icon(ft.Icons.HOME, color="#EE4D2D"),
                label="Home",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icon(ft.Icons.BROWSE_GALLERY_OUTLINED, color="#B0B0B0"),
                selected_icon=ft.Icon(ft.Icons.BROWSE_GALLERY, color="#EE4D2D"),
                label="Browse",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icon(ft.Icons.COLLECTIONS_OUTLINED, color="#B0B0B0"),
                selected_icon=ft.Icon(ft.Icons.COLLECTIONS, color="#EE4D2D"),
                label="Sammlungen",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icon(ft.Icons.STORAGE_OUTLINED, color="#B0B0B0"),
                selected_icon=ft.Icon(ft.Icons.STORAGE, color="#EE4D2D"),
                label="Datenbank",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icon(ft.Icons.SETTINGS_OUTLINED, color="#B0B0B0"),
                selected_icon=ft.Icon(ft.Icons.SETTINGS, color="#EE4D2D"),
                label="Einstellungen",
            ),
        ],
        on_change=on_nav_change,
    )
    
    # Content area
    content = ft.Container(
        content=ft.Text("Pr0-Archiv - Phase 1: Database & Migration", color="#FFFFFF", size=24),
        expand=True,
        padding=20,
    )
    
    # Responsive layout
    def on_resize(e):
        width = page.width or 0  # Handle None case
        if width < 800:
            rail.visible = False
            nav_bar.visible = True
        else:
            rail.visible = True
            nav_bar.visible = False
        page.update()
    
    page.on_resize = on_resize
    
    # Initial check
    on_resize(None)
    
    # Layout
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1, color="#333333"),
                ft.Column([content], expand=True),
            ],
            expand=True,
        ),
        nav_bar,
    )


if __name__ == "__main__":
    ft.run(main)