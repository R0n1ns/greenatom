# База данных
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_, update, and_, exists

from app.db.models import User, CreateUserPD, ChatMessage, MessagePD
from dotenv import load_dotenv
load_dotenv("app/.env")
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Зависимость для подключения к базе данных
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Пользователь
async def get_user(username: str, db: AsyncSession):
    query = select(User).filter(User.username == username)
    result = await db.execute(query)
    return result.scalars().first()
# Проверка на существование пользователя
async def user_exists(username: str, db: AsyncSession) -> bool:
    query = select(exists().where(User.username == username))
    result = await db.execute(query)
    return result.scalar()

async def create_user(user: CreateUserPD, db: AsyncSession):
    db_user = User(username=user.username, password=user.password, mail=user.mail, name=user.name)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def create_admin(user: CreateUserPD, db: AsyncSession):
    db_user = User(username=user.username, password=user.password, mail=user.mail, name=user.name,is_admin=True)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def is_blocked(username: str, db: AsyncSession):
    query = select(User.is_blocked).where(User.username == username)
    result = await db.execute(query)
    return result.scalar()  # Это безопасно, так как данные всегда извлекаются заново


async def is_admin(username: str, db: AsyncSession):
    user = await get_user(username, db)
    return user.is_admin if user else None

# Сообщения
# Получить все сообщения из чатов пользователя
async def get_user_messages(username: str, is_readed: bool = None, db: AsyncSession = None, chat: bool = True):
    """
    Получает сообщения пользователя в формате словаря.

    :param username: имя пользователя
    :param is_readed: True - прочитанные, False - непрочитанные, ничего - все
    :param chat: True - формат чата (от этого пользователя и ему), False - только отправленные сообщения
    :return: словарь сообщений
    """
    # Фильтрация сообщений в зависимости от значения параметра chat
    if chat:
        query = select(ChatMessage).filter(
            or_(ChatMessage.user_from_username == username, ChatMessage.user_to_username == username)
        )
    else:
        query = select(ChatMessage).filter(ChatMessage.user_to_username == username)

    # Выполнение запроса
    result = await db.execute(query)
    messages_data = result.scalars().all()
    messages = {}

    # Формирование словаря сообщений с учётом параметра is_readed
    for message in messages_data:
        if is_readed is not None and message.is_read != is_readed:
            continue

        # Ключ - имя другого пользователя в чате
        key = message.user_to_username if message.user_from_username == username else message.user_from_username
        if key not in messages:
            messages[key] = []

        messages[key].append({
            "from": message.user_from_username,
            "to": message.user_to_username,
            "text": message.message_text,
            "is_read": message.is_read,
            "date": message.date
        })

    # Сортировка сообщений по дате
    for key in messages:
        messages[key] = sorted(messages[key], key=lambda msg: msg["date"])

    return messages

# Добавить сообщение пользователя
async def add_message(message: MessagePD, db: AsyncSession):
    if await user_exists(message.user_to_username,db):
        new_mess = ChatMessage(
            user_from_username=message.user_from_username,
            user_to_username=message.user_to_username,
            message_text=message.message_text
        )
        db.add(new_mess)
        await db.commit()
        return True,new_mess.id
    else:
        return False,"Ошибка отправки сообщения"

# Прочитать сообщение
async def read_message(id: int, db: AsyncSession):
    query = update(ChatMessage).where(ChatMessage.id == id).values(is_read=True)
    await db.execute(query)
    await db.commit()

# Прочитать все сообщения от конкретного пользователя
async def read_all_messages_from_user(username: str, username_from: str, db: AsyncSession):
    query = update(ChatMessage).where(
        and_(ChatMessage.is_read == False, ChatMessage.user_to_username == username, ChatMessage.user_from_username == username_from)
    ).values(is_read=True)
    await db.execute(query)
    await db.commit()

# Прочитать все сообщения для пользователя
async def read_all_messages(username: str, db: AsyncSession):
    query = update(ChatMessage).where(
        and_(ChatMessage.is_read == False, ChatMessage.user_to_username == username)
    ).values(is_read=True)
    await db.execute(query)
    await db.commit()

async def block_user(username: str, db: AsyncSession):
    query = update(User).where(User.username == username).values(is_blocked=True)
    await db.execute(query)
    await db.commit()
    # Явно просрочиваем объект в кэше (необязательно, если is_blocked всегда читает заново)
    await db.refresh(await get_user(username, db))

# Разблокировать пользователя
async def unblock_user(username: str, db: AsyncSession):
    query = update(User).where(User.username == username).values(is_blocked=False)
    await db.execute(query)
    await db.commit()
