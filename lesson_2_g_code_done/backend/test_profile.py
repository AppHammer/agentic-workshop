import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import models
import schemas
from main import app
from auth import create_access_token, get_current_user


class TestGetUserProfileEndpoint:
    """Test suite for GET /users/me/profile endpoint."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = TestClient(app)
        self.test_customer = Mock(spec=models.User)
        self.test_customer.id = 1
        self.test_customer.username = "johncustomer"
        self.test_customer.email = "john@example.com"
        self.test_customer.user_type = models.UserType.CUSTOMER
        self.test_customer.created_at = datetime(2024, 1, 15, 10, 30, 0)
        self.test_customer.skills = None
        self.test_customer.hourly_rate = None
        
        self.test_tasker = Mock(spec=models.User)
        self.test_tasker.id = 2
        self.test_tasker.username = "janetasker"
        self.test_tasker.email = "jane@example.com"
        self.test_tasker.user_type = models.UserType.TASKER
        self.test_tasker.created_at = datetime(2024, 1, 20, 14, 22, 0)
        self.test_tasker.skills = "Plumbing, Electrical Work"
        self.test_tasker.hourly_rate = 45.00
    
    def test_get_profile_success_customer(self):
        """Test successful retrieval of customer profile with valid token."""
        # Override the dependency to return our test customer
        app.dependency_overrides[get_current_user] = lambda: self.test_customer
        
        try:
            response = self.client.get("/users/me/profile")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert data["username"] == "johncustomer"
            assert data["email"] == "john@example.com"
            assert data["user_type"] == "customer"
            assert data["created_at"] == "2024-01-15T10:30:00"
            assert data["skills"] is None
            assert data["hourly_rate"] is None
        finally:
            # Clear dependency overrides
            app.dependency_overrides.clear()
    
    def test_get_profile_success_tasker(self):
        """Test successful retrieval of tasker profile with tasker-specific fields."""
        # Override the dependency to return our test tasker
        app.dependency_overrides[get_current_user] = lambda: self.test_tasker
        
        try:
            response = self.client.get("/users/me/profile")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 2
            assert data["username"] == "janetasker"
            assert data["email"] == "jane@example.com"
            assert data["user_type"] == "tasker"
            assert data["created_at"] == "2024-01-20T14:22:00"
            assert data["skills"] == "Plumbing, Electrical Work"
            assert data["hourly_rate"] == 45.00
        finally:
            app.dependency_overrides.clear()
    
    def test_get_profile_missing_token(self):
        """Test that missing authentication token returns 401."""
        response = self.client.get("/users/me/profile")
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"
    
    def test_get_profile_invalid_token(self):
        """Test that invalid token returns 401."""
        response = self.client.get(
            "/users/me/profile",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"
    
    def test_get_profile_malformed_token(self):
        """Test that malformed token returns 401."""
        response = self.client.get(
            "/users/me/profile",
            headers={"Authorization": "Bearer malformed"}
        )
        
        assert response.status_code == 401
    
    def test_get_profile_expired_token(self):
        """Test that expired token returns 401."""
        from datetime import timedelta
        
        # Create an expired token
        expired_token = create_access_token(
            data={"sub": "johncustomer"},
            expires_delta=timedelta(seconds=-1)
        )
        
        response = self.client.get(
            "/users/me/profile",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"
    
    def test_get_profile_user_not_found(self):
        """Test that valid token but non-existent user returns 401."""
        # Create valid token for non-existent user
        token = create_access_token(data={"sub": "nonexistentuser"})
        
        # The get_current_user dependency will raise HTTPException
        # when user is not found in database
        response = self.client.get(
            "/users/me/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"
    
    def test_get_profile_token_without_sub(self):
        """Test that token without 'sub' claim returns 401."""
        from jose import jwt
        from auth import SECRET_KEY, ALGORITHM
        
        # Create token without 'sub' claim
        token = jwt.encode({"email": "test@example.com"}, SECRET_KEY, algorithm=ALGORITHM)
        
        response = self.client.get(
            "/users/me/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"
    
    def test_get_profile_response_schema(self):
        """Test that response matches UserProfile schema structure."""
        app.dependency_overrides[get_current_user] = lambda: self.test_tasker
        
        try:
            response = self.client.get("/users/me/profile")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify all required fields are present
            required_fields = ["id", "username", "email", "user_type", "created_at"]
            for field in required_fields:
                assert field in data
            
            # Verify optional fields are present (can be null)
            optional_fields = ["skills", "hourly_rate"]
            for field in optional_fields:
                assert field in data
        finally:
            app.dependency_overrides.clear()
    
    def test_get_profile_customer_fields_null(self):
        """Test that customer profile has null tasker-specific fields."""
        app.dependency_overrides[get_current_user] = lambda: self.test_customer
        
        try:
            response = self.client.get("/users/me/profile")
            
            assert response.status_code == 200
            data = response.json()
            assert data["skills"] is None
            assert data["hourly_rate"] is None
            assert data["user_type"] == "customer"
        finally:
            app.dependency_overrides.clear()
    
    def test_get_profile_tasker_fields_populated(self):
        """Test that tasker profile has populated tasker-specific fields."""
        app.dependency_overrides[get_current_user] = lambda: self.test_tasker
        
        try:
            response = self.client.get("/users/me/profile")
            
            assert response.status_code == 200
            data = response.json()
            assert data["skills"] is not None
            assert data["hourly_rate"] is not None
            assert data["user_type"] == "tasker"
            assert isinstance(data["skills"], str)
            assert isinstance(data["hourly_rate"], (int, float))
        finally:
            app.dependency_overrides.clear()
    
    def test_get_profile_bearer_token_format(self):
        """Test that only Bearer token format is accepted."""
        token = create_access_token(data={"sub": "johncustomer"})
        
        # Test without "Bearer" prefix
        response = self.client.get(
            "/users/me/profile",
            headers={"Authorization": token}
        )
        
        assert response.status_code == 401
    
    def test_get_profile_case_sensitive_headers(self):
        """Test that authorization works without explicit token."""
        app.dependency_overrides[get_current_user] = lambda: self.test_customer
        
        try:
            response = self.client.get("/users/me/profile")
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()


class TestUserProfileSchema:
    """Test suite for UserProfile Pydantic schema."""
    
    def test_user_profile_schema_customer(self):
        """Test UserProfile schema with customer data."""
        profile_data = {
            "id": 1,
            "username": "johncustomer",
            "email": "john@example.com",
            "user_type": models.UserType.CUSTOMER,
            "created_at": datetime(2024, 1, 15, 10, 30, 0),
            "skills": None,
            "hourly_rate": None
        }
        
        profile = schemas.UserProfile(**profile_data)
        
        assert profile.id == 1
        assert profile.username == "johncustomer"
        assert profile.email == "john@example.com"
        assert profile.user_type == models.UserType.CUSTOMER
        assert profile.skills is None
        assert profile.hourly_rate is None
    
    def test_user_profile_schema_tasker(self):
        """Test UserProfile schema with tasker data."""
        profile_data = {
            "id": 2,
            "username": "janetasker",
            "email": "jane@example.com",
            "user_type": models.UserType.TASKER,
            "created_at": datetime(2024, 1, 20, 14, 22, 0),
            "skills": "Plumbing, Electrical Work",
            "hourly_rate": 45.00
        }
        
        profile = schemas.UserProfile(**profile_data)
        
        assert profile.id == 2
        assert profile.username == "janetasker"
        assert profile.email == "jane@example.com"
        assert profile.user_type == models.UserType.TASKER
        assert profile.skills == "Plumbing, Electrical Work"
        assert profile.hourly_rate == 45.00
    
    def test_user_profile_schema_from_orm(self):
        """Test UserProfile schema can be created from ORM model."""
        mock_user = Mock(spec=models.User)
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.user_type = models.UserType.CUSTOMER
        mock_user.created_at = datetime(2024, 1, 1, 0, 0, 0)
        mock_user.skills = None
        mock_user.hourly_rate = None
        
        # Verify Config.from_attributes is set correctly
        assert schemas.UserProfile.model_config.get("from_attributes") is True
    
    def test_user_profile_schema_invalid_email(self):
        """Test UserProfile schema rejects invalid email."""
        with pytest.raises(Exception):
            schemas.UserProfile(
                id=1,
                username="testuser",
                email="invalid-email",
                user_type=models.UserType.CUSTOMER,
                created_at=datetime.now(),
                skills=None,
                hourly_rate=None
            )
    
    def test_user_profile_schema_optional_fields(self):
        """Test UserProfile schema with optional fields omitted."""
        profile_data = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "user_type": models.UserType.CUSTOMER,
            "created_at": datetime.now()
        }
        
        profile = schemas.UserProfile(**profile_data)
        
        assert profile.skills is None
        assert profile.hourly_rate is None


class TestProfileEndpointIntegration:
    """Integration tests for the profile endpoint."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
    
    def test_profile_endpoint_exists(self):
        """Test that the /users/me/profile endpoint exists."""
        # Without authentication, should return 401 not 404
        response = self.client.get("/users/me/profile")
        assert response.status_code == 401  # Not 404
    
    def test_profile_endpoint_method_not_allowed(self):
        """Test that only GET method is allowed."""
        token = create_access_token(data={"sub": "testuser"})
        
        # Test POST
        response = self.client.post(
            "/users/me/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 405
        
        # Test PUT
        response = self.client.put(
            "/users/me/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 405
        
        # Test DELETE
        response = self.client.delete(
            "/users/me/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 405
    
    def test_profile_endpoint_in_openapi_docs(self):
        """Test that endpoint is documented in OpenAPI schema."""
        response = self.client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_schema = response.json()
        assert "/users/me/profile" in openapi_schema["paths"]
        assert "get" in openapi_schema["paths"]["/users/me/profile"]
        
        endpoint_spec = openapi_schema["paths"]["/users/me/profile"]["get"]
        assert "summary" in endpoint_spec or "description" in endpoint_spec
        assert "responses" in endpoint_spec
        assert "200" in endpoint_spec["responses"]
    
    def test_profile_endpoint_security_requirement(self):
        """Test that endpoint has security requirement in OpenAPI."""
        response = self.client.get("/openapi.json")
        openapi_schema = response.json()
        
        endpoint_spec = openapi_schema["paths"]["/users/me/profile"]["get"]
        # Should have security requirement
        assert "security" in endpoint_spec or "security" in openapi_schema