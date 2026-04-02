"""
Auth endpoint tests — registration, login, and profile.
"""

import pytest


class TestRegister:
    """POST /api/v1/auth/register"""

    def test_register_success(self, client):
        """New user registration should succeed and return a token."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepass123",
                "name": "New User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["user"]["email"] == "newuser@example.com"
        assert data["data"]["user"]["role"] == "viewer"  # default role
        assert "access_token" in data["data"]["token"]
        # Password should never appear in response
        assert "password" not in str(data)
        assert "hashed_password" not in str(data)

    def test_register_duplicate_email(self, client):
        """Registering with an existing email should fail with 409."""
        payload = {
            "email": "dupe@example.com",
            "password": "securepass123",
            "name": "First User",
        }
        client.post("/api/v1/auth/register", json=payload)

        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 409
        assert response.json()["success"] is False

    def test_register_invalid_email(self, client):
        """Invalid email format should fail validation."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "securepass123",
                "name": "Test",
            },
        )
        assert response.status_code == 422

    def test_register_short_password(self, client):
        """Password under 8 chars should fail validation."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "short",
                "name": "Test",
            },
        )
        assert response.status_code == 422

    def test_register_missing_fields(self, client):
        """Missing required fields should fail validation."""
        response = client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422


class TestLogin:
    """POST /api/v1/auth/login"""

    def test_login_success(self, client):
        """Login with correct credentials should return a token."""
        # First register
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "password": "securepass123",
                "name": "Login Test",
            },
        )

        # Then login
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "login@example.com", "password": "securepass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]["token"]

    def test_login_wrong_password(self, client):
        """Wrong password should return 401."""
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrongpass@example.com",
                "password": "securepass123",
                "name": "Test",
            },
        )

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "wrongpass@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Login with non-existent email should return 401."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "whatever"},
        )
        assert response.status_code == 401


class TestProfile:
    """GET /api/v1/auth/me"""

    def test_get_profile_authenticated(self, client):
        """Authenticated user should get their profile."""
        # Register and get token
        reg_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "profile@example.com",
                "password": "securepass123",
                "name": "Profile Test",
            },
        )
        token = reg_response.json()["data"]["token"]["access_token"]

        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["email"] == "profile@example.com"

    def test_get_profile_unauthenticated(self, client):
        """Unauthenticated request should return 401."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_get_profile_invalid_token(self, client):
        """Invalid token should return 401."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token-here"},
        )
        assert response.status_code == 401
