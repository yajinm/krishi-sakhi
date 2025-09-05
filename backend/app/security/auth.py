"""
JWT authentication utilities.

Handles token creation, verification, and user authentication.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create JWT access token.
    
    Args:
        subject: Subject (usually user ID)
        expires_delta: Token expiration time
        additional_claims: Additional claims to include
        
    Returns:
        JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    # Load private key
    with open(settings.jwt_private_key_path, "r") as key_file:
        private_key = key_file.read()
    
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create JWT refresh token.
    
    Args:
        subject: Subject (usually user ID)
        expires_delta: Token expiration time
        
    Returns:
        JWT refresh token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    }
    
    # Load private key
    with open(settings.jwt_private_key_path, "r") as key_file:
        private_key = key_file.read()
    
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify JWT token and return payload.
    
    Args:
        token: JWT token string
        token_type: Expected token type (access or refresh)
        
    Returns:
        Token payload if valid, None otherwise
    """
    try:
        # Load public key
        with open(settings.jwt_public_key_path, "r") as key_file:
            public_key = key_file.read()
        
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": True},
        )
        
        # Check token type
        if payload.get("type") != token_type:
            return None
        
        return payload
        
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def create_token_pair(user_id: uuid.UUID, additional_claims: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """
    Create access and refresh token pair.
    
    Args:
        user_id: User ID
        additional_claims: Additional claims for access token
        
    Returns:
        Dictionary with access_token and refresh_token
    """
    access_token = create_access_token(
        subject=str(user_id),
        additional_claims=additional_claims,
    )
    
    refresh_token = create_refresh_token(subject=str(user_id))
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def extract_user_id_from_token(token: str) -> Optional[uuid.UUID]:
    """
    Extract user ID from JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        User ID if valid, None otherwise
    """
    payload = verify_token(token)
    if payload and "sub" in payload:
        try:
            return uuid.UUID(payload["sub"])
        except ValueError:
            return None
    return None


def is_token_expired(token: str) -> bool:
    """
    Check if token is expired.
    
    Args:
        token: JWT token string
        
    Returns:
        True if expired, False otherwise
    """
    payload = verify_token(token)
    if not payload:
        return True
    
    exp = payload.get("exp")
    if not exp:
        return True
    
    return datetime.utcnow() > datetime.fromtimestamp(exp)


def get_token_expiry(token: str) -> Optional[datetime]:
    """
    Get token expiry time.
    
    Args:
        token: JWT token string
        
    Returns:
        Expiry datetime if valid, None otherwise
    """
    payload = verify_token(token)
    if not payload:
        return None
    
    exp = payload.get("exp")
    if not exp:
        return None
    
    return datetime.fromtimestamp(exp)
