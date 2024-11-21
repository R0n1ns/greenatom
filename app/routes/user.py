from fastapi import  Depends, HTTPException, status, APIRouter
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import  UserPD
from app.db.queries import get_user, get_user_messages, read_all_messages ,read_all_messages_from_user, get_db
from app.routes.auth import oauth2_scheme
from app.routes.utils import  SECRET_KEY, ALGORITHM

user_router = APIRouter()

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(username, db)
    if user is None or user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Blocked")
    return user


@user_router.get("/getallmessages", summary="получить все сообщения", tags=["Получение истории сообщений"])
async def getallmessages(current_user: UserPD = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    chats = await get_user_messages(current_user.username, db = db,chat = False)
    return chats

@user_router.get("/getallchats", summary="получить все чаты", tags=["Получение истории сообщений"])
async def getallchats(current_user: UserPD = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    chats = await get_user_messages(current_user.username, db = db)
    return chats

@user_router.get("/getreadedmessages", summary="получить все прочитанные сообщения", tags=["Получение истории сообщений"])
async def getreadedmessages(current_user: UserPD = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    chats = await get_user_messages(current_user.username,True, db,False)
    return chats


@user_router.get("/getnotreadedmessages", summary="получить все непрочитанные сообщения", tags=["Получение истории сообщений"])
async def getnotreadedmessages(current_user: UserPD = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    chats = await get_user_messages(current_user.username,False, db,False)
    return chats


@user_router.post("/readnotreaded", summary="прочитать все непрочитанные сообщения", tags=["Получение истории сообщений"])
async def readnotreaded(current_user: UserPD = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        await read_all_messages(current_user.username, db)
        return status.HTTP_200_OK
    except Exception:
        return status.HTTP_500_INTERNAL_SERVER_ERROR


@user_router.post("/readnotreadedfromuser", summary="прочитать все непрочитанные сообщения от пользователя", tags=["Получение истории сообщений"])
async def readnotreadedfromuser(user_from: str, current_user: UserPD = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        await read_all_messages_from_user(current_user.username, user_from, db)
        return status.HTTP_200_OK
    except Exception:
        return status.HTTP_500_INTERNAL_SERVER_ERROR

