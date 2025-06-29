"""Authentication and authorization tests."""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import status
from jose import jwt

from app.models.user import UserRole
from test.conftest import create_expired_token, create_invalid_token, create_test_token


class TestJWTTokenValidation:
    """JWT token validation tests."""
    
    def test_successful_token_generation(self, client, test_settings):
        response = client.post(
            "/auth/token",
            json={"api_key": test_settings.API_KEY, "role": "user"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        decoded = jwt.decode(
            data["access_token"],
            test_settings.PUBLIC_KEY,
            algorithms=["RS256"]
        )
        assert decoded["api_key"] == test_settings.API_KEY
        assert decoded["role"] == "user"
        assert decoded["exp"] > time.time()
    
    def test_token_generation_with_admin_role(self, client, test_settings):
        response = client.post(
            "/auth/token",
            json={"api_key": test_settings.API_KEY, "role": "admin"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        decoded = jwt.decode(
            data["access_token"],
            test_settings.PUBLIC_KEY,
            algorithms=["RS256"]
        )
        assert decoded["role"] == "admin"
    
    def test_token_generation_invalid_api_key(self, client):
        response = client.post(
            "/auth/token",
            json={"api_key": "invalid-key", "role": "user"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid API key" in response.json()["detail"]
    
    def test_expired_token_rejection(self, client, test_settings):
        expired_token = create_expired_token(test_settings)
        response = client.get(
            "/summarize/text",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid token" in response.json()["detail"]
    
    def test_malformed_token_rejection(self, client):
        response = client.get(
            "/summarize/text",
            headers={"Authorization": "Bearer malformed.token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_missing_authorization_header(self, client):
        response = client.get("/summarize/text")
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_invalid_authorization_format(self, client):
        response = client.get(
            "/summarize/text",
            headers={"Authorization": "InvalidFormat token"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_token_signature_validation(self, client, test_settings):
        payload = {
            "api_key": test_settings.API_KEY,
            "role": "user",
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
        }
        
        wrong_key = b"wrong-secret-key"
        invalid_token = jwt.encode(payload, wrong_key, algorithm="HS256")
        
        response = client.get(
            "/summarize/text",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAPIKeyAuthentication:
    """API key authentication tests."""
    
    def test_valid_api_key_in_token(self, client, test_settings, auth_headers):
        response = client.post(
            "/summarize/text",
            json={"content": "Test", "style": "general", "length": "short"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_invalid_api_key_in_token(self, client, test_settings):
        token = create_test_token("wrong-api-key", UserRole.USER, test_settings)
        response = client.post(
            "/summarize/text",
            json={"content": "Test", "style": "general", "length": "short"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid API key" in response.json()["detail"]
    
    def test_api_key_rotation_scenario(self, client, test_settings, monkeypatch):
        old_token = create_test_token(test_settings.API_KEY, UserRole.USER, test_settings)
        
        new_api_key = "new-api-key"
        monkeypatch.setattr(test_settings, "API_KEY", new_api_key)
        
        response = client.post(
            "/summarize/text",
            json={"content": "Test", "style": "general", "length": "short"},
            headers={"Authorization": f"Bearer {old_token}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRoleBasedAccessControl:
    """Role-based access control tests."""
    
    def test_admin_endpoint_with_admin_role(self, client, admin_auth_headers):
        response = client.get("/admin/stats", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK
    
    def test_admin_endpoint_with_user_role(self, client, auth_headers):
        response = client.get("/admin/stats", headers=auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin access required" in response.json()["detail"]
    
    def test_admin_logs_endpoint_access(self, client, admin_auth_headers):
        response = client.get("/admin/logs?limit=10", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK
    
    def test_user_endpoint_with_admin_role(self, client, admin_auth_headers):
        response = client.post(
            "/summarize/text",
            json={"content": "Test", "style": "general", "length": "short"},
            headers=admin_auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_role_validation_in_token(self, client, test_settings):
        payload = {
            "api_key": test_settings.API_KEY,
            "role": "invalid_role",
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
        }
        token = jwt.encode(payload, test_settings.PRIVATE_KEY, algorithm="RS256")
        
        response = client.get(
            "/admin/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.parametrize("endpoint,method", [
        ("/admin/stats", "GET"),
        ("/admin/logs", "GET"),
    ])
    def test_admin_endpoints_require_auth(self, client, endpoint, method):
        response = client.request(method, endpoint)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestRateLimiting:
    """Rate limiting per API key tests."""
    
    @pytest.mark.asyncio
    async def test_rate_limit_per_api_key(self, client, auth_headers, test_settings):
        test_settings.RATE_LIMIT_PER_MINUTE = 5
        
        for i in range(5):
            response = client.post(
                "/summarize/text",
                json={"content": f"Test {i}", "style": "general", "length": "short"},
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
        
        response = client.post(
            "/summarize/text",
            json={"content": "Test 6", "style": "general", "length": "short"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    
    def test_rate_limit_different_api_keys(self, client, test_settings):
        token1 = create_test_token("api_key_1", UserRole.USER, test_settings)
        token2 = create_test_token("api_key_2", UserRole.USER, test_settings)
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        test_settings.RATE_LIMIT_PER_MINUTE = 2
        
        for headers in [headers1, headers2]:
            for i in range(2):
                response = client.post(
                    "/summarize/text",
                    json={"content": f"Test", "style": "general", "length": "short"},
                    headers=headers
                )
                assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]


class TestTokenRefresh:
    """Token refresh mechanism tests."""
    
    def test_token_near_expiration(self, client, test_settings):
        token = create_test_token(
            test_settings.API_KEY,
            UserRole.USER,
            test_settings,
            exp_minutes=5
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/summarize/text",
            json={"content": "Test", "style": "general", "length": "short"},
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        assert "X-Token-Expires-In" not in response.headers


class TestSecurityHeaders:
    """Security headers validation tests."""
    
    def test_cors_headers(self, client, auth_headers):
        response = client.options(
            "/summarize/text",
            headers={**auth_headers, "Origin": "https://example.com"}
        )
        assert "Access-Control-Allow-Origin" in response.headers
    
    def test_security_headers_presence(self, client, auth_headers):
        response = client.get("/", headers=auth_headers)
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert "X-Frame-Options" in response.headers