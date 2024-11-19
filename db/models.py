import datetime

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

# Пользователь
class User(Base):
    __tablename__ = "users"

    username = Column(String,primary_key=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    mail = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_blocked = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    sent_messages = relationship("ChatMessage",
                                 foreign_keys='ChatMessage.user_from_username',
                                 back_populates="sender")
    received_messages = relationship("ChatMessage",
                                     foreign_keys='ChatMessage.user_to_username',
                                     back_populates="receiver")
# Сообщения в чате
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_from_username = Column(String, ForeignKey("users.username"), nullable=False)
    user_to_username = Column(String, ForeignKey("users.username"), nullable=False)
    message_text = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    sender = relationship("User", foreign_keys=[user_from_username], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[user_to_username], back_populates="received_messages")


# Модели для Pydantic
class UserPD(BaseModel):
    username: str
    name: str
    mail: str
    password: str
    is_admin:str

# Модели для Pydantic
class CreateUserPD(BaseModel):
    username: str
    name: str
    mail: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class MessagePD(BaseModel):
    message_text:str
    user_from_username:str
    user_to_username:str

