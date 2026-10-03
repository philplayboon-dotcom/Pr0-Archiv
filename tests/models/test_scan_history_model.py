from __future__ import annotations

from core.models import ScanHistory


class TestScanHistoryModel:
    """Unit tests for ScanHistory Pydantic model."""

    def test_scan_history_valid(self):
        """Test valid ScanHistory creation."""
        sh = ScanHistory(
            id=1,
            scan_type="initial",
            status="running",
            started_at="2026-01-01T12:00:00Z",
        )
        assert sh.scan_type == "initial"
        assert sh.status == "running"
        assert sh.fetched_count is None

    def test_scan_history_with_config_snapshot(self):
        """Test ScanHistory with config_snapshot."""
        config = {"mode": "initial", "flags": 7, "limit": 1000}
        sh = ScanHistory(
            id=1,
            scan_type="initial",
            status="completed",
            started_at="2026-01-01T12:00:00Z",
            config_snapshot=config,
        )
        assert sh.config_snapshot == config