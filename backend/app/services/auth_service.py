import uuid
from jose import jwt, JWTError
from app.core.config import settings
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError, InvalidTokenError, TokenExpiredError
from app.schemas.user import UserCreate
from app.schemas.auth import UserLogin, TokenPair
from app.repositories.user_repository import UserRepository
from app.models.user import User

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, user_create: UserCreate) -> User:
        existing_user = await self.user_repo.get_by_email(user_create.email)
        if existing_user:
            raise UserAlreadyExistsError()
        return await self.user_repo.create(user_create)

    async def authenticate(self, user_login: UserLogin) -> TokenPair:
        user = await self.user_repo.get_by_email(user_login.email)
        if not user or not verify_password(user_login.password, user.hashed_password):
            raise InvalidCredentialsError()
            
        jti = str(uuid.uuid4())
        access_token = create_access_token(subject=user.id, jti=jti)
        refresh_token = create_refresh_token(subject=user.id, jti=jti)
        
        return TokenPair(access_token=access_token, refresh_token=refresh_token)
        
    async def refresh_token(self, refresh_token: str) -> TokenPair:
        try:
            payload = jwt.decode(refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("sub")
            token_type = payload.get("type")
            jti = payload.get("jti")
            if user_id is None or token_type != "refresh":
                raise InvalidTokenError()
                
            from app.core.security import is_jti_blacklisted
            if await is_jti_blacklisted(jti):
                raise InvalidTokenError()
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except JWTError:
            raise InvalidTokenError()
            
        user = await self.user_repo.get_by_id(uuid.UUID(user_id))
        if not user:
            raise InvalidTokenError()
            
        jti = str(uuid.uuid4())
        new_access_token = create_access_token(subject=user.id, jti=jti)
        new_refresh_token = create_refresh_token(subject=user.id, jti=jti)
        
        return TokenPair(access_token=new_access_token, refresh_token=new_refresh_token)
