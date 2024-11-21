# Настройки
import datetime
import os
from datetime import timedelta
from typing import Dict

from fastapi import status, WebSocket
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import  MessagePD
from app.db.queries import add_message, read_message, is_blocked
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Функция создания токена
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, username: str, websocket: WebSocket, db: AsyncSession):
        if await is_blocked(username, db):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        await websocket.accept()
        self.active_connections[username] = websocket

    async def disconnect(self, username: str):
        websocket = self.active_connections.pop(username, None)
        if websocket and not websocket.client_state.closed:
            await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)

    async def broadcast(self, username_from: str, username_to: str, message: str, db: AsyncSession):
        if await is_blocked(username_from, db):
            await self.disconnect(username_from)
            return True

        mess = MessagePD(message_text=message, user_from_username=username_from, user_to_username=username_to)
        message_id = await add_message(mess, db)
        if not message_id[0]:
            await self.active_connections[username_from].send_json({"status":"error","error":message_id[1]})
            return
        else:
            message_id = message_id[1]

        data = {"username_from": username_from, "message": message}
        if username_to in self.active_connections.keys():
            await self.active_connections[username_to].send_json(data)
            await read_message(message_id, db)
        await self.active_connections[username_from].send_json({"status": "success", "error": None})
        return



    def get_active_users(self):
        return list(self.active_connections.keys())

ws_manager = ConnectionManager()
