import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
from jose import jwt, JWTError
from fastapi import HTTPException
from sqlalchemy.orm import Session
import models
from auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


class TestPasswordHashing:
    """Test suite for password hashing and verification functions."""
    
    def test_get_password_hash_returns_string(self):
        """Test that get_password_hash returns a string."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_get_password_hash_different_for_same_password(self):
        """Test that hashing the same password twice produces different hashes (salt)."""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        # Hashes should be different due to salt
        assert hash1 != hash2
    
    def test_verify_password_correct_password(self):
        """Test that verify_password returns True for correct password."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect_password(self):
        """Test that verify_password returns False for incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty_password(self):
        """Test verify_password with empty password."""
        hashed = get_password_hash("testpassword123")
        assert verify_password("", hashed) is False
    
    def test_get_password_hash_special_characters(self):
        """Test hashing password with special characters."""
        password = "P@ssw0rd!#$%^&*()"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
    
    def test_get_password_hash_unicode_characters(self):
        """Test hashing password with unicode characters."""
        password = "密码测试🔐"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True


class TestCreateAccessToken:
    """Test suite for JWT token creation."""
    
    def test_create_access_token_with_data(self):
        """Test creating access token with user data."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"
        assert "exp" in payload
    
    def test_create_access_token_default_expiration(self):
        """Test that token has default expiration of 15 minutes when not specified."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        
        # Should expire in approximately 15 minutes (with some tolerance)
        expected_exp = datetime.utcnow() + timedelta(minutes=15)
        time_diff = abs((exp_datetime - expected_exp).total_seconds())
        assert time_diff < 5  # Allow 5 seconds tolerance
    
    def test_create_access_token_custom_expiration(self):
        """Test creating token with custom expiration time."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires_delta)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        
        # Should expire in approximately 30 minutes
        expected_exp = datetime.utcnow() + timedelta(minutes=30)
        time_diff = abs((exp_datetime - expected_exp).total_seconds())
        assert time_diff < 5  # Allow 5 seconds tolerance
    
    def test_create_access_token_preserves_original_data(self):
        """Test that original data dict is not modified."""
        data = {"sub": "testuser", "role": "admin"}
        original_data = data.copy()
        
        create_access_token(data)
        
        # Original data should not be modified
        assert data == original_data
    
    def test_create_access_token_with_multiple_claims(self):
        """Test creating token with multiple claims."""
        data = {
            "sub": "testuser",
            "email": "test@example.com",
            "user_type": "customer"
        }
        token = create_access_token(data)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"
        assert payload["email"] == "test@example.com"
        assert payload["user_type"] == "customer"
    
    def test_create_access_token_zero_expiration(self):
        """Test creating token with zero expiration (immediate expiry)."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(seconds=0)
        token = create_access_token(data, expires_delta=expires_delta)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        
        # Token should be expired or about to expire
        assert exp_datetime <= datetime.utcnow() + timedelta(seconds=1)


class TestGetCurrentUser:
    """Test suite for get_current_user function."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_db = Mock(spec=Session)
        self.test_user = Mock(spec=models.User)
        self.test_user.id = 1
        self.test_user.username = "testuser"
        self.test_user.email = "test@example.com"
    
    def test_get_current_user_valid_token(self):
        """Test getting current user with valid token."""
        # Create a valid token
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        # Mock database query
        mock_query = self.mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = self.test_user
        
        # Call the function
        user = get_current_user(token=token, db=self.mock_db)
        
        assert user == self.test_user
        self.mock_db.query.assert_called_once_with(models.User)
    
    def test_get_current_user_invalid_token(self):
        """Test that invalid token raises HTTPException."""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=invalid_token, db=self.mock_db)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate credentials"
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
    
    def test_get_current_user_expired_token(self):
        """Test that expired token raises HTTPException."""
        # Create an expired token
        data = {"sub": "testuser"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta=expires_delta)
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=self.mock_db)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate credentials"
    
    def test_get_current_user_token_without_sub(self):
        """Test that token without 'sub' claim raises HTTPException."""
        # Create token without 'sub' claim
        data = {"email": "test@example.com"}
        token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=self.mock_db)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate credentials"
    
    def test_get_current_user_user_not_found_in_db(self):
        """Test that non-existent user raises HTTPException."""
        data = {"sub": "nonexistentuser"}
        token = create_access_token(data)
        
        # Mock database query to return None
        mock_query = self.mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=self.mock_db)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate credentials"
    
    def test_get_current_user_malformed_token(self):
        """Test that malformed token raises HTTPException."""
        malformed_token = "not.a.valid.jwt.token.format"
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=malformed_token, db=self.mock_db)
        
        assert exc_info.value.status_code == 401
    
    def test_get_current_user_token_with_wrong_algorithm(self):
        """Test that token signed with wrong algorithm raises HTTPException."""
        data = {"sub": "testuser"}
        # Create token with different algorithm
        wrong_token = jwt.encode(data, SECRET_KEY, algorithm="HS512")
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=wrong_token, db=self.mock_db)
        
        assert exc_info.value.status_code == 401
    
    def test_get_current_user_token_with_wrong_secret(self):
        """Test that token signed with wrong secret raises HTTPException."""
        data = {"sub": "testuser"}
        # Create token with wrong secret
        wrong_token = jwt.encode(data, "wrong-secret-key", algorithm=ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=wrong_token, db=self.mock_db)
        
        assert exc_info.value.status_code == 401


class TestAuthConstants:
    """Test suite for authentication constants."""
    
    def test_secret_key_exists(self):
        """Test that SECRET_KEY is defined."""
        assert SECRET_KEY is not None
        assert len(SECRET_KEY) > 0
    
    def test_algorithm_is_hs256(self):
        """Test that ALGORITHM is HS256."""
        assert ALGORITHM == "HS256"
    
    def test_access_token_expire_minutes(self):
        """Test that ACCESS_TOKEN_EXPIRE_MINUTES is defined."""
        assert ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert isinstance(ACCESS_TOKEN_EXPIRE_MINUTES, int)


class TestIntegration:
    """Integration tests combining multiple auth functions."""
    
    def test_full_auth_flow(self):
        """Test complete authentication flow: hash password, create token, verify user."""
        # Step 1: Hash a password
        password = "securepassword123"
        hashed_password = get_password_hash(password)
        
        # Step 2: Verify the password
        assert verify_password(password, hashed_password) is True
        
        # Step 3: Create access token
        user_data = {"sub": "testuser"}
        token = create_access_token(user_data)
        
        # Step 4: Decode token manually to verify
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"
        assert "exp" in payload
    
    def test_password_hash_uniqueness_across_users(self):
        """Test that same password creates different hashes for different users."""
        password = "commonpassword"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        hash3 = get_password_hash(password)
        
        # All hashes should be different (due to salt)
        assert hash1 != hash2
        assert hash2 != hash3
        assert hash1 != hash3
        
        # But all should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
        assert verify_password(password, hash3) is True