"""
Authentication router.

Handles OTP-based authentication and JWT token management.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.deps import CurrentUser, DatabaseSession
from app.models import User
from app.security import create_token_pair, generate_otp, verify_otp, get_or_create_user_by_phone

router = APIRouter()


class OTPStartRequest(BaseModel):
    """Request model for starting OTP flow."""
    phone: str = Field(..., description="Phone number with country code")


class OTPStartResponse(BaseModel):
    """Response model for OTP start."""
    req_id: str = Field(..., description="Request ID for OTP verification")
    message: str = Field(..., description="Status message")
    expires_in: int = Field(..., description="OTP expiration time in seconds")


class OTPVerifyRequest(BaseModel):
    """Request model for OTP verification."""
    req_id: str = Field(..., description="Request ID from OTP start")
    code: str = Field(..., description="OTP code")


class OTPVerifyResponse(BaseModel):
    """Response model for OTP verification."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    user: dict = Field(..., description="User information")


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str = Field(..., description="JWT refresh token")


class RefreshTokenResponse(BaseModel):
    """Response model for token refresh."""
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


@router.post("/otp/start", response_model=OTPStartResponse)
async def start_otp_flow(
    request: OTPStartRequest,
    session: DatabaseSession,
):
    """
    Start OTP authentication flow.
    
    Sends OTP to the provided phone number for authentication.
    """
    phone = request.phone.strip()
    
    # Validate phone number format
    if not phone.startswith("+") or len(phone) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format. Use international format (+91xxxxxxxxxx)"
        )
    
    try:
        # Generate OTP
        otp_code = generate_otp(phone)
        
        # In production, this would send SMS via Twilio or other provider
        # For now, we'll just return the OTP in development
        if settings.dev_mode:
            print(f"🔐 OTP for {phone}: {otp_code}")
        
        # Generate request ID
        req_id = str(uuid.uuid4())
        
        # Store request ID in Redis (simplified for demo)
        # In production, this would be stored with expiration
        
        return OTPStartResponse(
            req_id=req_id,
            message="OTP sent successfully",
            expires_in=300,  # 5 minutes
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP"
        )


@router.post("/otp/verify", response_model=OTPVerifyResponse)
async def verify_otp_code(
    request: OTPVerifyRequest,
    session: DatabaseSession,
):
    """
    Verify OTP code and return JWT tokens.
    
    Verifies the OTP code and returns access and refresh tokens.
    """
    # In production, this would validate the req_id and get phone from it
    # For demo, we'll use a simple approach
    
    try:
        # For demo purposes, we'll use a hardcoded phone
        # In production, this would be retrieved from the req_id
        phone = "+919876543210"  # Demo phone number
        
        # Verify OTP
        if not verify_otp(phone, request.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP code"
            )
        
        # Get or create user
        user = await get_or_create_user_by_phone(phone)
        
        # Create token pair
        tokens = create_token_pair(
            user_id=user.id,
            additional_claims={
                "phone": user.phone,
                "role": user.role.value,
            }
        )
        
        return OTPVerifyResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            user={
                "id": str(user.id),
                "phone": user.phone,
                "role": user.role.value,
                "locale": user.locale,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat(),
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify OTP"
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
):
    """
    Refresh access token using refresh token.
    
    Generates a new access token using the provided refresh token.
    """
    from app.security import verify_token, create_access_token
    
    # Verify refresh token
    payload = verify_token(request.refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Extract user ID
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Create new access token
    access_token = create_access_token(
        subject=user_id,
        additional_claims={
            "phone": payload.get("phone"),
            "role": payload.get("role"),
        }
    )
    
    return RefreshTokenResponse(
        access_token=access_token,
        token_type="bearer"
    )


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: CurrentUser,
):
    """
    Get current user information.
    
    Returns information about the currently authenticated user.
    """
    return {
        "id": str(current_user.id),
        "phone": current_user.phone,
        "role": current_user.role.value,
        "locale": current_user.locale,
        "consent_flags": current_user.consent_flags,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
        "created_at": current_user.created_at.isoformat(),
        "updated_at": current_user.updated_at.isoformat(),
    }


@router.post("/logout")
async def logout(
    current_user: CurrentUser,
):
    """
    Logout current user.
    
    Invalidates the current session (client should discard tokens).
    """
    # In production, this would invalidate the token in Redis
    # For now, we'll just return success
    
    return {
        "message": "Logged out successfully",
        "user_id": str(current_user.id)
    }
