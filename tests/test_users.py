"""
User management endpoint tests — RBAC enforcement and CRUD.
"""

import pytest
from tests.conftest import create_test_user, get_auth_header


class TestListUsers:
    """GET /api/v1/users"""

    def test_admin_can_list_users(self, client, admin_headers, db):
        """Admin should see all users."""
        # Create additional users
        create_test_user(db, role="analyst", email="analyst2@test.com")
        create_test_user(db, role="viewer", email="viewer2@test.com")

        response = client.get("/api/v1/users", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 3  # admin + analyst + viewer
        assert "meta" in data  # pagination metadata

    def test_viewer_cannot_list_users(self, client, viewer_headers):
        """Viewer should be forbidden from listing users."""
        response = client.get("/api/v1/users", headers=viewer_headers)
        assert response.status_code == 403

    def test_analyst_cannot_list_users(self, client, analyst_headers):
        """Analyst should be forbidden from listing users."""
        response = client.get("/api/v1/users", headers=analyst_headers)
        assert response.status_code == 403

    def test_unauthenticated_cannot_list_users(self, client):
        """Unauthenticated request should return 401."""
        response = client.get("/api/v1/users")
        assert response.status_code == 401


class TestUpdateUser:
    """PATCH /api/v1/users/{id}"""

    def test_admin_can_update_user_role(self, client, admin_headers, db):
        """Admin should be able to change a user's role."""
        user = create_test_user(db, role="viewer", email="update_me@test.com")

        response = client.patch(
            f"/api/v1/users/{user.id}",
            json={"role": "analyst"},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["data"]["role"] == "analyst"

    def test_admin_can_deactivate_user(self, client, admin_headers, db):
        """Admin should be able to set a user to inactive."""
        user = create_test_user(db, role="viewer", email="deactivate@test.com")

        response = client.patch(
            f"/api/v1/users/{user.id}",
            json={"status": "inactive"},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "inactive"

    def test_update_nonexistent_user(self, client, admin_headers):
        """Updating a non-existent user should return 404."""
        response = client.patch(
            "/api/v1/users/nonexistent-id",
            json={"name": "Ghost"},
            headers=admin_headers,
        )
        assert response.status_code == 404


class TestDeleteUser:
    """DELETE /api/v1/users/{id}"""

    def test_admin_can_delete_user(self, client, admin_headers, db):
        """Admin should be able to soft-delete a user."""
        user = create_test_user(db, role="viewer", email="delete_me@test.com")

        response = client.delete(
            f"/api/v1/users/{user.id}",
            headers=admin_headers,
        )
        assert response.status_code == 200

        # Verify user is no longer listable
        list_response = client.get("/api/v1/users", headers=admin_headers)
        emails = [u["email"] for u in list_response.json()["data"]]
        assert "delete_me@test.com" not in emails

    def test_admin_cannot_self_delete(self, client, admin_user, admin_headers):
        """Admin should not be able to delete their own account."""
        response = client.delete(
            f"/api/v1/users/{admin_user.id}",
            headers=admin_headers,
        )
        assert response.status_code == 400
