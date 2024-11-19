from datetime import timedelta

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Token, CreateUserPD
from db.queries import get_user, create_user,get_db
from routes.utils import create_access_token,  ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
auth_router = APIRouter()
@auth_router.post("/register", response_model=Token, tags=["Авторизация"], summary="Регистрация")
async def register(user: CreateUserPD, db: AsyncSession = Depends(get_db)):
    db_user = await get_user(user.username, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    await create_user(user, db)
    access_token = create_access_token(data={"username": user.username, "is_admin": False})
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/login", response_model=Token, tags=["Авторизация"], summary="Авторизация")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user(form_data.username, db)
    if not user or form_data.password != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"username": user.username, "is_admin": user.is_admin},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}
