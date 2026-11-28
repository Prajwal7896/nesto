from dotenv import load_dotenv
import os

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    TIMESTAMP,
    func
)
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel, EmailStr

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, nullable=False)

    password_hash = Column(String(255), nullable=False)

    phone_number = Column(String(15), unique=True, nullable=True)

    age = Column(Integer, nullable=True)

    role = Column(String(50), nullable=True)

    image_url = Column(Text, nullable=True)

    subscription_plan = Column(String(20), default="FREE")

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password_hash: str
    phone_number: str | None = None
    age: int | None = None
    role: str = "User"
    image_url: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str