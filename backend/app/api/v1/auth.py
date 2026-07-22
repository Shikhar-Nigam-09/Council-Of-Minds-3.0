from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead
from app.schemas.auth import UserLogin, TokenPair, TokenRefreshRequest
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.api.deps import get_current_user
from app.models.user import User
from app.core.rate_limiter import rate_limit_general

router = APIRouter()

def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))

@router.post("/register", dependencies=[Depends(rate_limit_general)])
async def register(user_create: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    user = await auth_service.register(user_create)
    return {"success": True, "data": UserRead.model_validate(user).model_dump(mode="json")}

@router.post("/login", dependencies=[Depends(rate_limit_general)])
async def login(user_login: UserLogin, auth_service: AuthService = Depends(get_auth_service)):
    tokens = await auth_service.authenticate(user_login)
    return {"success": True, "data": tokens.model_dump()}

@router.post("/refresh")
async def refresh(refresh_req: TokenRefreshRequest, auth_service: AuthService = Depends(get_auth_service)):
    tokens = await auth_service.refresh_token(refresh_req.refresh_token)
    return {"success": True, "data": tokens.model_dump()}

from app.api.deps import oauth2_scheme

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    from jose import jwt
    from app.core.config import settings
    from app.core.security import blacklist_jti
    from datetime import datetime, timedelta
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": False})
        jti = payload.get("jti")
        if jti:
            max_exp = int((datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).timestamp())
            await blacklist_jti(jti, max_exp)
    except Exception:
        pass

    return {"success": True, "data": {"message": "Logged out successfully"}}

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {"success": True, "data": UserRead.model_validate(current_user).model_dump(mode="json")}
