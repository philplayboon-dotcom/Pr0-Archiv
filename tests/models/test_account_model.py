from __future__ import annotations

from core.models import Account


class TestAccountModel:
    """Unit tests for Account Pydantic model."""

    def test_account_valid(self):
        """Test valid Account creation."""
        acc = Account(
            id=1,
            username="testuser",
            cookie_hash="abc123",
            display_name="Test User"
        )
        assert acc.username == "testuser"
        assert acc.cookie_hash == "abc123"
        assert acc.display_name == "Test User"
        assert acc.is_active is True

    def test_account_minimal(self):
        """Test Account with only required fields."""
        acc = Account(id=1, username="minimal", cookie_hash="hash")
        assert acc.username == "minimal"
        assert acc.cookie_hash == "hash"
        assert acc.display_name is None
        assert acc.last_login is None
        assert acc.is_active is True
        assert acc.created_at is None