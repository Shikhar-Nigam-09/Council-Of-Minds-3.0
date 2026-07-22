import pytest
from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_password
import uuid

def test_password_hashing():
    password = "MySecurePassword123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_creation():
    user_id = str(uuid.uuid4())
    jti = str(uuid.uuid4())
    access = create_access_token(user_id, jti)
    refresh = create_refresh_token(user_id, jti)
    
    assert access is not None
    assert refresh is not None
    assert type(access) == str
    assert type(refresh) == str
