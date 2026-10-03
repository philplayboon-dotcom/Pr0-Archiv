from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_create_scan_history(fresh_db, scan_history_repo):
    """Test creating a scan history entry."""
    sh = await scan_history_repo.create(
        scan_type="initial",
        status="running",
        started_at="2026-01-01T12:00:00Z",
    )
    assert sh is not None
    assert sh.id is not None
    assert sh.scan_type == "initial"
    assert sh.status == "running"


async def test_get_latest(fresh_db, scan_history_repo):
    """Test get_latest returns most recent scan."""
    await scan_history_repo.create(
        scan_type="initial", status="completed", started_at="2026-01-01T10:00:00Z"
    )
    await scan_history_repo.create(
        scan_type="incremental", status="running", started_at="2026-01-01T12:00:00Z"
    )
    
    latest = await scan_history_repo.get_latest()
    assert latest is not None
    assert latest.scan_type == "incremental"
    assert latest.started_at == "2026-01-01T12:00:00Z"


async def test_get_by_type(fresh_db, scan_history_repo):
    """Test get_by_type returns scans of specific type."""
    await scan_history_repo.create(scan_type="initial", status="completed", started_at="2026-01-01T10:00:00Z")
    await scan_history_repo.create(scan_type="initial", status="completed", started_at="2026-01-01T11:00:00Z")
    await scan_history_repo.create(scan_type="backfill", status="running", started_at="2026-01-01T12:00:00Z")
    
    initial_scans = await scan_history_repo.get_by_type("initial")
    assert len(initial_scans) == 2
    
    backfill_scans = await scan_history_repo.get_by_type("backfill")
    assert len(backfill_scans) == 1
    assert backfill_scans[0].scan_type == "backfill"


async def test_update_scan_status(fresh_db, scan_history_repo):
    """Test updating scan status."""
    sh = await scan_history_repo.create(
        scan_type="initial", status="running", started_at="2026-01-01T12:00:00Z"
    )
    
    updated = await scan_history_repo.update(
        sh.id,
        status="completed",
        completed_at="2026-01-01T12:05:00Z",
        fetched_count=100,
        new_count=95,
        duplicate_count=5,
    )
    assert updated.status == "completed"
    assert updated.fetched_count == 100
    assert updated.new_count == 95
    assert updated.duplicate_count == 5