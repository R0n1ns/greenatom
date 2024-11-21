import asyncio

from fastapi import FastAPI, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CreateUserPD
from app.db.queries import get_user, get_db, create_admin, user_exists, AsyncSessionLocal
from app.routes.admin import admin_router
from app.routes.auth import auth_router
from app.routes.user import user_router
from app.routes.utils import SECRET_KEY, ALGORITHM, ws_manager

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



@app.on_event("startup")
async def startup_event():
    # Открываем сессию через AsyncSessionLocal напрямую
    async with AsyncSessionLocal() as db:
        # Пример данных администратора
        admin_data = CreateUserPD(
            username="admin",
            name="Admin User",
            mail="admin@example.com",
            password="securepassword"
        )
        # Если администратор не найден, создаем нового
        if not await user_exists(admin_data.username, db):
            await create_admin(admin_data, db)

app.include_router(admin_router)
app.include_router(user_router)
app.include_router(auth_router)

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    token = websocket.headers.get("Authorization")
    if token is None or not token.startswith("Bearer "):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    token = token.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        user = await get_user(username, db)
        if user is None or user.is_blocked:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await ws_manager.connect(username, websocket, db)

        try:
            while True:
                data = await websocket.receive_json()

                res = await ws_manager.broadcast(username, data["username_to"], data["message"], db)
                if res:
                    break


        except WebSocketDisconnect:
            print(username)
            await ws_manager.disconnect(username)
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
