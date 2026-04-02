"""
Financial records endpoint tests — CRUD, filtering, and RBAC.
"""

import pytest
from tests.conftest import get_auth_header


SAMPLE_RECORD = {
    "amount": 1500.00,
    "type": "income",
    "category": "Salary",
    "date": "2024-06-15",
    "description": "Monthly salary payment",
}


class TestCreateRecord:
    """POST /api/v1/records"""

    def test_admin_can_create_record(self, client, admin_headers):
        """Admin should be able to create a financial record."""
        response = client.post(
            "/api/v1/records", json=SAMPLE_RECORD, headers=admin_headers
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["amount"] == 1500.00
        assert data["type"] == "income"
        assert data["category"] == "Salary"

    def test_viewer_cannot_create_record(self, client, viewer_headers):
        """Viewer should be forbidden from creating records."""
        response = client.post(
            "/api/v1/records", json=SAMPLE_RECORD, headers=viewer_headers
        )
        assert response.status_code == 403

    def test_analyst_cannot_create_record(self, client, analyst_headers):
        """Analyst should be forbidden from creating records."""
        response = client.post(
            "/api/v1/records", json=SAMPLE_RECORD, headers=analyst_headers
        )
        assert response.status_code == 403

    def test_create_record_invalid_amount(self, client, admin_headers):
        """Negative amount should fail validation."""
        bad_record = {**SAMPLE_RECORD, "amount": -100}
        response = client.post(
            "/api/v1/records", json=bad_record, headers=admin_headers
        )
        assert response.status_code == 422

    def test_create_record_invalid_type(self, client, admin_headers):
        """Invalid type should fail validation."""
        bad_record = {**SAMPLE_RECORD, "type": "unknown"}
        response = client.post(
            "/api/v1/records", json=bad_record, headers=admin_headers
        )
        assert response.status_code == 422

    def test_create_record_missing_fields(self, client, admin_headers):
        """Missing required fields should fail validation."""
        response = client.post(
            "/api/v1/records", json={}, headers=admin_headers
        )
        assert response.status_code == 422


class TestListRecords:
    """GET /api/v1/records"""

    def test_all_roles_can_list_records(
        self, client, admin_headers, analyst_headers, viewer_headers
    ):
        """All authenticated roles should be able to list records."""
        # Create a record first
        client.post("/api/v1/records", json=SAMPLE_RECORD, headers=admin_headers)

        for headers in [admin_headers, analyst_headers, viewer_headers]:
            response = client.get("/api/v1/records", headers=headers)
            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_filter_by_type(self, client, admin_headers):
        """Should filter records by income/expense type."""
        # Create both types
        client.post("/api/v1/records", json=SAMPLE_RECORD, headers=admin_headers)
        expense = {**SAMPLE_RECORD, "type": "expense", "category": "Food", "amount": 50}
        client.post("/api/v1/records", json=expense, headers=admin_headers)

        response = client.get(
            "/api/v1/records?type=income", headers=admin_headers
        )
        assert response.status_code == 200
        records = response.json()["data"]
        assert all(r["type"] == "income" for r in records)

    def test_filter_by_date_range(self, client, admin_headers):
        """Should filter records by date range."""
        client.post("/api/v1/records", json=SAMPLE_RECORD, headers=admin_headers)

        response = client.get(
            "/api/v1/records?start_date=2024-06-01&end_date=2024-06-30",
            headers=admin_headers,
        )
        assert response.status_code == 200

    def test_pagination(self, client, admin_headers):
        """Should return paginated results with metadata."""
        # Create multiple records
        for i in range(5):
            record = {**SAMPLE_RECORD, "amount": 100 + i, "date": f"2024-06-{10+i:02d}"}
            client.post("/api/v1/records", json=record, headers=admin_headers)

        response = client.get(
            "/api/v1/records?page=1&limit=2", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["meta"]["total"] == 5
        assert data["meta"]["has_next"] is True

    def test_search_in_description(self, client, admin_headers):
        """Should search within record descriptions."""
        client.post("/api/v1/records", json=SAMPLE_RECORD, headers=admin_headers)

        response = client.get(
            "/api/v1/records?search=salary", headers=admin_headers
        )
        assert response.status_code == 200
        assert len(response.json()["data"]) >= 1

    def test_unauthenticated_cannot_list(self, client):
        """Unauthenticated request should return 401."""
        response = client.get("/api/v1/records")
        assert response.status_code == 401


class TestUpdateRecord:
    """PATCH /api/v1/records/{id}"""

    def test_admin_can_update_record(self, client, admin_headers):
        """Admin should be able to update a record."""
        create_resp = client.post(
            "/api/v1/records", json=SAMPLE_RECORD, headers=admin_headers
        )
        record_id = create_resp.json()["data"]["id"]

        response = client.patch(
            f"/api/v1/records/{record_id}",
            json={"amount": 2000.00, "category": "Bonus"},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["data"]["amount"] == 2000.00
        assert response.json()["data"]["category"] == "Bonus"

    def test_viewer_cannot_update_record(self, client, admin_headers, viewer_headers):
        """Viewer should be forbidden from updating records."""
        create_resp = client.post(
            "/api/v1/records", json=SAMPLE_RECORD, headers=admin_headers
        )
        record_id = create_resp.json()["data"]["id"]

        response = client.patch(
            f"/api/v1/records/{record_id}",
            json={"amount": 9999},
            headers=viewer_headers,
        )
        assert response.status_code == 403


class TestDeleteRecord:
    """DELETE /api/v1/records/{id}"""

    def test_admin_can_delete_record(self, client, admin_headers):
        """Admin should be able to soft-delete a record."""
        create_resp = client.post(
            "/api/v1/records", json=SAMPLE_RECORD, headers=admin_headers
        )
        record_id = create_resp.json()["data"]["id"]

        response = client.delete(
            f"/api/v1/records/{record_id}", headers=admin_headers
        )
        assert response.status_code == 200

        # Verify record is no longer returned
        get_resp = client.get(
            f"/api/v1/records/{record_id}", headers=admin_headers
        )
        assert get_resp.status_code == 404

    def test_delete_nonexistent_record(self, client, admin_headers):
        """Deleting a non-existent record should return 404."""
        response = client.delete(
            "/api/v1/records/nonexistent-id", headers=admin_headers
        )
        assert response.status_code == 404
