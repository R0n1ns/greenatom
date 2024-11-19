from fastapi import  Depends, HTTPException, status, APIRouter
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import  UserPD
from db.queries import get_user, get_user_messages, block_user, unblock_user,get_db
from routes.auth import oauth2_scheme
from routes.utils import SECRET_KEY, ALGORITHM,ws_manager

admin_router = APIRouter()

async def get_current_admin(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
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
    if user is None or user.is_blocked or not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access")
    return user


@admin_router.get("/readuserchats", summary="получить все чаты пользователя", tags=["Команды админа"])
async def readuserchats(username: str, current_user: UserPD = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    chats = await get_user_messages(username, db=db)
    return chats


@admin_router.get("/getallactiveusers", summary="получить всех активных пользователей", tags=["Команды админа"])
async def getallactiveusers(current_user: UserPD = Depends(get_current_admin)):
    return ws_manager.get_active_users()


@admin_router.get("/blockuser", summary="заблокировать пользователя", tags=["Команды админа"])
async def blockuser(username: str, current_user: UserPD = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    try:
        await block_user(username, db)
        return status.HTTP_200_OK
    except Exception:
        return status.HTTP_500_INTERNAL_SERVER_ERROR


@admin_router.get("/unblockuser", summary="разблокировать пользователя", tags=["Команды админа"])
async def unblockuser(username: str, current_user: UserPD = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    try:
        await unblock_user(username, db)
        return status.HTTP_200_OK
    except Exception:
        return status.HTTP_500_INTERNAL_SERVER_ERROR

