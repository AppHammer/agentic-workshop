import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from pydantic import ValidationError

import models
import schemas
from main import app, update_user_profile
from auth import create_access_token, get_current_user

client = TestClient(app)


class TestUpdateUserProfile:
    """Test suite for the update_user_profile endpoint."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_db = Mock(spec=Session)
        self.test_user = Mock(spec=models.User)
        self.test_user.id = 1
        self.test_user.username = "testuser"
        self.test_user.email = "test@example.com"
        self.test_user.user_type = models.UserType.TASKER
        self.test_user.skills = "Plumbing, Carpentry"
        self.test_user.hourly_rate = 50.0
    
    def test_update_profile_success_all_fields(self):
        """Test successful profile update with all fields."""
        # Create update data
        update_data = schemas.UserUpdate(
            email="newemail@example.com",
            skills="Plumbing, Carpentry, Electrical",
            hourly_rate=75.0
        )
        
        # Call the endpoint
        result = update_user_profile(
            user_data=update_data,
            current_user=self.test_user,
            db=self.mock_db
        )
        
        # Verify database operations
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once_with(self.test_user)
        
        # Verify user attributes were updated
        assert self.test_user.email == "newemail@example.com"
        assert self.test_user.skills == "Plumbing, Carpentry, Electrical"
        assert self.test_user.hourly_rate == 75.0
        
        # Verify the result
        assert result == self.test_user
    
    def test_update_profile_success_email_only(self):
        """Test successful profile update with email only."""
        update_data = schemas.UserUpdate(email="updated@example.com")
        
        result = update_user_profile(
            user_data=update_data,
            current_user=self.test_user,
            db=self.mock_db
        )
        
        # Verify only email was updated
        assert self.test_user.email == "updated@example.com"
        assert self.test_user.skills == "Plumbing, Carpentry"  # Unchanged
        assert self.test_user.hourly_rate == 50.0  # Unchanged
        
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()
    
    def test_update_profile_success_skills_only(self):
        """Test successful profile update with skills only."""
        update_data = schemas.UserUpdate(skills="New Skill Set")
        
        result = update_user_profile(
            user_data=update_data,
            current_user=self.test_user,
            db=self.mock_db
        )
        
        # Verify only skills was updated
        assert self.test_user.email == "test@example.com"  # Unchanged
        assert self.test_user.skills == "New Skill Set"
        assert self.test_user.hourly_rate == 50.0  # Unchanged
        
        self.mock_db.commit.assert_called_once()
    
    def test_update_profile_success_hourly_rate_only(self):
        """Test successful profile update with hourly_rate only."""
        update_data = schemas.UserUpdate(hourly_rate=100.0)
        
        result = update_user_profile(
            user_data=update_data,
            current_user=self.test_user,
            db=self.mock_db
        )
        
        # Verify only hourly_rate was updated
        assert self.test_user.email == "test@example.com"  # Unchanged
        assert self.test_user.skills == "Plumbing, Carpentry"  # Unchanged
        assert self.test_user.hourly_rate == 100.0
        
        self.mock_db.commit.assert_called_once()
    
    def test_update_profile_success_empty_update(self):
        """Test profile update with no fields (should still succeed but change nothing)."""
        update_data = schemas.UserUpdate()
        
        result = update_user_profile(
            user_data=update_data,
            current_user=self.test_user,
            db=self.mock_db
        )
        
        # Verify nothing changed
        assert self.test_user.email == "test@example.com"
        assert self.test_user.skills == "Plumbing, Carpentry"
        assert self.test_user.hourly_rate == 50.0
        
        # Database operations should still occur
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()
    
    def test_update_profile_invalid_email(self):
        """Test that invalid email format raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            schemas.UserUpdate(email="not-a-valid-email")
        
        # Verify it's an email validation error
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert errors[0]['loc'] == ('email',)
        assert 'email' in errors[0]['msg'].lower() or 'value' in errors[0]['msg'].lower()
    
    def test_update_profile_negative_hourly_rate(self):
        """Test that negative hourly_rate raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            schemas.UserUpdate(hourly_rate=-10.0)
        
        # Verify it's a validation error for hourly_rate
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert errors[0]['loc'] == ('hourly_rate',)
    
    def test_update_profile_zero_hourly_rate(self):
        """Test that zero hourly_rate raises ValidationError (must be > 0)."""
        with pytest.raises(ValidationError) as exc_info:
            schemas.UserUpdate(hourly_rate=0.0)
        
        # Verify it's a validation error
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert errors[0]['loc'] == ('hourly_rate',)
    
    def test_update_profile_positive_hourly_rate_edge_case(self):
        """Test that very small positive hourly_rate is valid."""
        update_data = schemas.UserUpdate(hourly_rate=0.01)
        
        # Should not raise validation error
        assert update_data.hourly_rate == 0.01
        
        result = update_user_profile(
            user_data=update_data,
            current_user=self.test_user,
            db=self.mock_db
        )
        
        assert self.test_user.hourly_rate == 0.01
    
    def test_update_profile_large_hourly_rate(self):
        """Test that large hourly_rate values are accepted."""
        update_data = schemas.UserUpdate(hourly_rate=999999.99)
        
        result = update_user_profile(
            user_data=update_data,
            current_user=self.test_user,
            db=self.mock_db
        )
        
        assert self.test_user.hourly_rate == 999999.99
    
    def test_update_profile_special_characters_in_skills(self):
        """Test that special characters in skills are handled correctly."""
        skills_with_special = "C++, C#, .NET, React.js, Node.js"
        update_data = schemas.UserUpdate(skills=skills_with_special)
        
        result = update_user_profile(
            user_data=update_data,
            current_user=self.test_user,
            db=self.mock_db
        )
        
        assert self.test_user.skills == skills_with_special
    
    def test_update_profile_unicode_in_skills(self):
        """Test that unicode characters in skills are handled correctly."""
        skills_with_unicode = "水管工, 木工, Électricien"
        update_data = schemas.UserUpdate(skills=skills_with_unicode)
        
        result = update_user_profile(
            user_data=update_data,
            current_user=self.test_user,
            db=self.mock_db
        )
        
        assert self.test_user.skills == skills_with_unicode
    
    def test_update_profile_empty_skills_string(self):
        """Test that empty skills string is accepted."""
        update_data = schemas.UserUpdate(skills="")
        
        result = update_user_profile(
            user_data=update_data,
            current_user=self.test_user,
            db=self.mock_db
        )
        
        assert self.test_user.skills == ""
    
    def test_update_profile_whitespace_skills(self):
        """Test that whitespace-only skills are accepted."""
        update_data = schemas.UserUpdate(skills="   ")
        
        result = update_user_profile(
            user_data=update_data,
            current_user=self.test_user,
            db=self.mock_db
        )
        
        assert self.test_user.skills == "   "
    
    def test_update_profile_very_long_skills(self):
        """Test that very long skills strings are accepted."""
        long_skills = ", ".join([f"Skill{i}" for i in range(100)])
        update_data = schemas.UserUpdate(skills=long_skills)
        
        result = update_user_profile(
            user_data=update_data,
            current_user=self.test_user,
            db=self.mock_db
        )
        
        assert self.test_user.skills == long_skills
    
    def test_update_profile_multiple_email_formats(self):
        """Test various valid email formats."""
        valid_emails = [
            "simple@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "user_name@example.com",
            "123@example.com",
            "user@subdomain.example.com"
        ]
        
        for email in valid_emails:
            update_data = schemas.UserUpdate(email=email)
            result = update_user_profile(
                user_data=update_data,
                current_user=self.test_user,
                db=self.mock_db
            )
            assert self.test_user.email == email
    
    def test_update_profile_database_commit_called(self):
        """Test that database commit is called."""
        update_data = schemas.UserUpdate(email="new@example.com")
        
        update_user_profile(
            user_data=update_data,
            current_user=self.test_user,
            db=self.mock_db
        )
        
        self.mock_db.commit.assert_called_once()
    
    def test_update_profile_database_refresh_called(self):
        """Test that database refresh is called with the user."""
        update_data = schemas.UserUpdate(email="new@example.com")
        
        update_user_profile(
            user_data=update_data,
            current_user=self.test_user,
            db=self.mock_db
        )
        
        self.mock_db.refresh.assert_called_once_with(self.test_user)
    
    def test_update_profile_returns_updated_user(self):
        """Test that the endpoint returns the updated user object."""
        update_data = schemas.UserUpdate(
            email="updated@example.com",
            skills="Updated Skills",
            hourly_rate=80.0
        )
        
        result = update_user_profile(
            user_data=update_data,
            current_user=self.test_user,
            db=self.mock_db
        )
        
        assert result is self.test_user
        assert result.email == "updated@example.com"
        assert result.skills == "Updated Skills"
        assert result.hourly_rate == 80.0


class TestUserUpdateSchema:
    """Test suite for UserUpdate Pydantic schema."""
    
    def test_user_update_schema_all_fields_optional(self):
        """Test that all fields in UserUpdate are optional."""
        # Should be able to create with no fields
        update = schemas.UserUpdate()
        assert update.email is None
        assert update.skills is None
        assert update.hourly_rate is None
    
    def test_user_update_schema_partial_fields(self):
        """Test creating schema with partial fields."""
        # Email only
        update1 = schemas.UserUpdate(email="test@example.com")
        assert update1.email == "test@example.com"
        assert update1.skills is None
        assert update1.hourly_rate is None
        
        # Skills only
        update2 = schemas.UserUpdate(skills="Test Skills")
        assert update2.email is None
        assert update2.skills == "Test Skills"
        assert update2.hourly_rate is None
        
        # Hourly rate only
        update3 = schemas.UserUpdate(hourly_rate=50.0)
        assert update3.email is None
        assert update3.skills is None
        assert update3.hourly_rate == 50.0
    
    def test_user_update_schema_exclude_unset(self):
        """Test that exclude_unset works correctly for partial updates."""
        update = schemas.UserUpdate(email="test@example.com")
        data = update.model_dump(exclude_unset=True)
        
        # Should only include email, not skills or hourly_rate
        assert "email" in data
        assert "skills" not in data
        assert "hourly_rate" not in data
        assert data["email"] == "test@example.com"
    
    def test_user_update_schema_email_validation(self):
        """Test email validation in schema."""
        # Valid email should work
        update = schemas.UserUpdate(email="valid@example.com")
        assert update.email == "valid@example.com"
        
        # Invalid email shouldraise ValidationError
        with pytest.raises(ValidationError):
            schemas.UserUpdate(email="invalid-email")
    
    def test_user_update_schema_hourly_rate_validation(self):
        """Test hourly_rate validation (must be > 0)."""
        # Valid positive rate
        update = schemas.UserUpdate(hourly_rate=50.0)
        assert update.hourly_rate == 50.0
        
        # Zero should fail
        with pytest.raises(ValidationError):
            schemas.UserUpdate(hourly_rate=0.0)
        
        # Negative should fail
        with pytest.raises(ValidationError):
            schemas.UserUpdate(hourly_rate=-10.0)
    
    def test_user_update_schema_skills_accepts_any_string(self):
        """Test that skills field accepts any string value."""
        test_skills = [
            "Simple Skills",
            "",
            "   ",
            "C++, C#, .NET",
            "Very " * 100 + "Long"
        ]
        
        for skill in test_skills:
            update = schemas.UserUpdate(skills=skill)
            assert update.skills == skill


class TestAuthenticationRequirement:
    """Test suite to verify authentication is required for the endpoint."""
    
    def test_endpoint_requires_authentication(self):
        """Test that the PUT /users/me endpoint requires authentication."""
        # Make a request without authentication - should return 401
        response = client.put("/users/me", json={})
        assert response.status_code == 401, "Endpoint should require authentication"