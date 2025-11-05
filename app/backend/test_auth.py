import pytest
from datetime import timedelta
from jose import jwt
import auth


class TestPasswordHashing:
    """Tests for password hashing and verification"""
    
    def test_hash_password_normal(self):
        """Test hashing a normal length password"""
        password = "mySecurePassword123"
        hashed = auth.get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
        
    def test_hash_password_short(self):
        """Test hashing a very short password"""
        password = "abc"
        hashed = auth.get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password
        
    def test_hash_password_long(self):
        """Test hashing a very long password (>72 bytes)"""
        password = "a" * 100  # 100 character password
        hashed = auth.get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password
        
    def test_hash_password_special_chars(self):
        """Test hashing password with special characters"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = auth.get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password
        
    def test_hash_password_unicode(self):
        """Test hashing password with unicode characters"""
        password = "密码test123"
        hashed = auth.get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password
        
    def test_hash_same_password_different_hashes(self):
        """Test that same password creates different hashes (salt)"""
        password = "samePassword123"
        hash1 = auth.get_password_hash(password)
        hash2 = auth.get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2


class TestPasswordVerification:
    """Tests for password verification"""
    
    def test_verify_correct_password(self):
        """Test verification with correct password"""
        password = "correctPassword123"
        hashed = auth.get_password_hash(password)
        
        assert auth.verify_password(password, hashed) is True
        
    def test_verify_incorrect_password(self):
        """Test verification with incorrect password"""
        password = "correctPassword123"
        wrong_password = "wrongPassword123"
        hashed = auth.get_password_hash(password)
        
        assert auth.verify_password(wrong_password, hashed) is False
        
    def test_verify_case_sensitive(self):
        """Test that password verification is case-sensitive"""
        password = "Password123"
        hashed = auth.get_password_hash(password)
        
        assert auth.verify_password("password123", hashed) is False
        assert auth.verify_password("PASSWORD123", hashed) is False
        assert auth.verify_password("Password123", hashed) is True
        
    def test_verify_long_password(self):
        """Test verification with long password (>72 bytes)"""
        password = "a" * 100
        hashed = auth.get_password_hash(password)
        
        assert auth.verify_password(password, hashed) is True
        
    def test_verify_empty_password_fails(self):
        """Test that empty password doesn't verify"""
        password = "normalPassword"
        hashed = auth.get_password_hash(password)
        
        assert auth.verify_password("", hashed) is False
        
    def test_verify_unicode_password(self):
        """Test verification with unicode password"""
        password = "密码test123"
        hashed = auth.get_password_hash(password)
        
        assert auth.verify_password(password, hashed) is True
        assert auth.verify_password("密码test124", hashed) is False


class TestAccessToken:
    """Tests for JWT access token creation and validation"""
    
    def test_create_access_token_basic(self):
        """Test creating a basic access token"""
        data = {"sub": "test@example.com"}
        token = auth.create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
    def test_create_access_token_with_expiry(self):
        """Test creating token with custom expiry"""
        data = {"sub": "test@example.com"}
        expires = timedelta(minutes=30)
        token = auth.create_access_token(data, expires_delta=expires)
        
        assert token is not None
        
    def test_token_contains_correct_data(self):
        """Test that token contains the correct payload data"""
        email = "test@example.com"
        data = {"sub": email}
        token = auth.create_access_token(data)
        
        # Decode token to verify contents
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        
        assert payload["sub"] == email
        assert "exp" in payload
        
    def test_token_has_expiration(self):
        """Test that token has expiration field"""
        data = {"sub": "test@example.com"}
        token = auth.create_access_token(data)
        
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        
        assert "exp" in payload
        assert isinstance(payload["exp"], (int, float))
        
    def test_different_users_different_tokens(self):
        """Test that different users get different tokens"""
        token1 = auth.create_access_token({"sub": "user1@example.com"})
        token2 = auth.create_access_token({"sub": "user2@example.com"})
        
        assert token1 != token2
        
    def test_token_with_additional_claims(self):
        """Test token creation with additional claims"""
        data = {
            "sub": "test@example.com",
            "role": "admin",
            "user_id": 123
        }
        token = auth.create_access_token(data)
        
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        
        assert payload["sub"] == "test@example.com"
        assert payload["role"] == "admin"
        assert payload["user_id"] == 123


class TestPasswordEdgeCases:
    """Tests for edge cases in password handling"""
    
    def test_password_at_72_byte_boundary(self):
        """Test password exactly at 72 bytes"""
        password = "a" * 72
        hashed = auth.get_password_hash(password)
        
        assert auth.verify_password(password, hashed) is True
        
    def test_password_just_over_72_bytes(self):
        """Test password just over 72 bytes"""
        password = "a" * 73
        hashed = auth.get_password_hash(password)
        
        assert auth.verify_password(password, hashed) is True
        
    def test_multibyte_characters_boundary(self):
        """Test multibyte characters near 72 byte limit"""
        # Japanese/Chinese characters are typically 3 bytes in UTF-8
        password = "密" * 24  # 24 * 3 = 72 bytes
        hashed = auth.get_password_hash(password)
        
        assert auth.verify_password(password, hashed) is True
        
    def test_very_long_password(self):
        """Test extremely long password"""
        password = "x" * 1000
        hashed = auth.get_password_hash(password)
        
        assert auth.verify_password(password, hashed) is True
        
    def test_password_with_null_bytes(self):
        """Test password handling with special characters"""
        password = "test\x00password"
        hashed = auth.get_password_hash(password)
        
        # This might behave differently depending on implementation
        # Just ensure no crash occurs
        assert hashed is not None


class TestConstants:
    """Tests for auth module constants"""
    
    def test_secret_key_exists(self):
        """Test that SECRET_KEY is defined"""
        assert hasattr(auth, 'SECRET_KEY')
        assert auth.SECRET_KEY is not None
        assert len(auth.SECRET_KEY) > 0
        
    def test_algorithm_exists(self):
        """Test that ALGORITHM is defined"""
        assert hasattr(auth, 'ALGORITHM')
        assert auth.ALGORITHM == "HS256"
        
    def test_token_expire_minutes_exists(self):
        """Test that ACCESS_TOKEN_EXPIRE_MINUTES is defined"""
        assert hasattr(auth, 'ACCESS_TOKEN_EXPIRE_MINUTES')
        assert isinstance(auth.ACCESS_TOKEN_EXPIRE_MINUTES, int)
        assert auth.ACCESS_TOKEN_EXPIRE_MINUTES > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])