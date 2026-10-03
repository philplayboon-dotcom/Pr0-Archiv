from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.models import Settings


class TestSettingsModel:
    """Unit tests for Settings Pydantic model."""

    def test_settings_valid(self):
        """Test valid Settings creation."""
        s = Settings(key="show_thumbnails", value="true")
        assert s.key == "show_thumbnails"
        assert s.value == "true"

    def test_settings_key_validation_strips_whitespace(self):
        """Test key validator strips whitespace."""
        s = Settings(key="  scan_limit  ", value="1000")
        assert s.key == "scan_limit"

    def test_settings_empty_key_raises(self):
        """Test empty key raises validation error."""
        try:
            Settings(key="", value="test")
            assert False, "Should have raised ValidationError"
        except ValidationError:
            pass  # Expected

    def test_settings_whitespace_only_key_raises(self):
        """Test whitespace-only key raises validation error."""
        try:
            Settings(key="   ", value="test")
            assert False, "Should have raised ValidationError"
        except ValidationError:
            pass  # Expected