from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, UserUpdate,
    Token, TokenRefresh
)
from app.services.auth_service import AuthService
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="创建新用户账号，注册后可使用用户名和密码登录",
    responses={
        201: {"description": "注册成功"},
        400: {"description": "请求参数错误"},
        409: {"description": "用户名已存在"},
    },
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await AuthService.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/login",
    response_model=Token,
    summary="用户登录",
    description="使用用户名和密码登录，返回 Access Token 和 Refresh Token",
    responses={
        200: {"description": "登录成功，返回JWT令牌"},
        401: {"description": "用户名或密码错误"},
    },
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    user = await AuthService.authenticate_user(
        db, credentials.username, credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {"sub": user.id, "username": user.username}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    payload = decode_token(token_data.refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    user_id = payload.get("sub")
    from app.services.auth_service import AuthService
    user = await AuthService.get_user_by_id(db, user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    new_token_data = {"sub": user.id, "username": user.username}
    access_token = create_access_token(new_token_data)
    new_refresh_token = create_refresh_token(new_token_data)

    return Token(access_token=access_token, refresh_token=new_refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        updated_user = await AuthService.update_user(db, current_user, update_data)
        return updated_user
    except Exception as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
