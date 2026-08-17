"""Authentication API router."""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_session_token, verify_session_token
from app.schemas import AuthResponse, LoginRequest, UserResponse
from app.services import session_service, user_service

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate a user via Immutable Passport.
    
    For Phase 1, we trust the Passport SDK proof from the frontend.
    Production should verify the proof server-side.
    """
    # Validate basic fields
    if not request.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required",
        )

    # Get or create user
    user, is_new_user = await user_service.get_or_create_user(
        db=db,
        email=request.email,
        passport_id=request.passport_proof,
        wallet_address=request.wallet_address,
    )

    # Create session token
    token = create_session_token(user.id)
    await session_service.create_session(user.id, token)

    return AuthResponse(
        user_id=user.id,
        session_token=token,
        is_new_user=is_new_user,
        lockdown_state={
            "is_active": True,
            "graduated_at": None,
            "care_actions_completed": 0,
            "min_bond_achieved": 0,
        },
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Get the current authenticated user's profile."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    
    token = authorization.replace("Bearer ", "")
    user_id = await session_service.validate_session(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )
    
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse.model_validate(user)


@router.post("/logout")
async def logout(authorization: str = None):
    """Revoke the current session."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        await session_service.revoke_session(token)
    return {"status": "logged_out"}
