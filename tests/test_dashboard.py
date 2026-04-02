"""
Dashboard endpoint tests — analytics and RBAC enforcement.
"""

import pytest
from tests.conftest import get_auth_header


def _seed_records(client, admin_headers):
    """Create a set of known records for predictable dashboard results."""
    records = [
        {"amount": 5000, "type": "income", "category": "Salary", "date": "2024-06-01", "description": "June salary"},
        {"amount": 2000, "type": "income", "category": "Freelance", "date": "2024-06-15", "description": "Project payment"},
        {"amount": 1200, "type": "expense", "category": "Housing", "date": "2024-06-01", "description": "Rent"},
        {"amount": 300, "type": "expense", "category": "Groceries", "date": "2024-06-10", "description": "Weekly groceries"},
        {"amount": 100, "type": "expense", "category": "Entertainment", "date": "2024-06-20", "description": "Movies"},
        {"amount": 4500, "type": "income", "category": "Salary", "date": "2024-07-01", "description": "July salary"},
        {"amount": 800, "type": "expense", "category": "Groceries", "date": "2024-07-15", "description": "Monthly groceries"},
    ]
    for record in records:
        client.post("/api/v1/records", json=record, headers=admin_headers)


class TestSummary:
    """GET /api/v1/dashboard/summary"""

    def test_analyst_can_access_summary(self, client, admin_headers, analyst_headers):
        """Analyst should access the financial summary."""
        _seed_records(client, admin_headers)

        response = client.get("/api/v1/dashboard/summary", headers=analyst_headers)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["total_income"] == 11500.0  # 5000 + 2000 + 4500
        assert data["total_expenses"] == 2400.0  # 1200 + 300 + 100 + 800
        assert data["net_balance"] == 9100.0
        assert data["total_records"] == 7

    def test_admin_can_access_summary(self, client, admin_headers):
        """Admin should access the financial summary."""
        response = client.get("/api/v1/dashboard/summary", headers=admin_headers)
        assert response.status_code == 200

    def test_viewer_cannot_access_summary(self, client, viewer_headers):
        """Viewer should be forbidden from dashboard analytics."""
        response = client.get("/api/v1/dashboard/summary", headers=viewer_headers)
        assert response.status_code == 403

    def test_unauthenticated_cannot_access_summary(self, client):
        """Unauthenticated request should return 401."""
        response = client.get("/api/v1/dashboard/summary")
        assert response.status_code == 401


class TestCategoryBreakdown:
    """GET /api/v1/dashboard/category-breakdown"""

    def test_returns_category_breakdown(self, client, admin_headers):
        """Should return per-category income/expense totals."""
        _seed_records(client, admin_headers)

        response = client.get(
            "/api/v1/dashboard/category-breakdown", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) >= 3  # Salary, Freelance, Housing, Groceries, Entertainment

        # Verify structure
        for item in data:
            assert "category" in item
            assert "total_income" in item
            assert "total_expense" in item
            assert "net" in item
            assert "record_count" in item

    def test_viewer_cannot_access(self, client, viewer_headers):
        """Viewer should be forbidden."""
        response = client.get(
            "/api/v1/dashboard/category-breakdown", headers=viewer_headers
        )
        assert response.status_code == 403


class TestMonthlyTrends:
    """GET /api/v1/dashboard/trends"""

    def test_returns_monthly_trends(self, client, admin_headers):
        """Should return monthly aggregates."""
        _seed_records(client, admin_headers)

        response = client.get("/api/v1/dashboard/trends", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) >= 1

        for item in data:
            assert "month" in item
            assert "total_income" in item
            assert "total_expense" in item
            assert "net" in item

    def test_viewer_cannot_access(self, client, viewer_headers):
        """Viewer should be forbidden."""
        response = client.get("/api/v1/dashboard/trends", headers=viewer_headers)
        assert response.status_code == 403


class TestRecentActivity:
    """GET /api/v1/dashboard/recent-activity"""

    def test_returns_recent_records(self, client, admin_headers):
        """Should return the most recent records."""
        _seed_records(client, admin_headers)

        response = client.get(
            "/api/v1/dashboard/recent-activity?limit=5", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) <= 5

    def test_viewer_cannot_access(self, client, viewer_headers):
        """Viewer should be forbidden."""
        response = client.get(
            "/api/v1/dashboard/recent-activity", headers=viewer_headers
        )
        assert response.status_code == 403
