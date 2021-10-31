import os
import jwt
from datetime import datetime, timedelta
from tortoise import fields, models
from passlib.context import CryptContext
from .exceptions import UserAlreadyExists
from tortoise.contrib.pydantic import pydantic_model_creator
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=32, unique=True, null=False)
    password_hash = fields.CharField(max_length=512, null=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    @classmethod
    async def create_user(cls, username, password):
        exists = await cls.filter(username=username).first()
        if exists:
            raise UserAlreadyExists
        hashed_password = pwd_context.hash(password)
        user = await cls.create(username=username, password_hash=hashed_password)
        return user

    async def verify_password(self, password):
        pwd_context.verify(password, self.password_hash)

    @classmethod
    async def authenticate_user(cls, username, password):
        user = await cls.filter(username=username).first()
        if user is None:
            return False
        if user.verify_password(password):
            return user
        return None

    async def create_access_token(self, expire_minutes=5, **data):
        payload = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
        payload.update({"user_id": self.id})
        payload.update({"exp": expire})
        encoded_jwt = jwt.encode(payload, SECRET_KEY, "HS256")
        return encoded_jwt

    class PydanticMeta:
        exclude = ["password_hash"]




user_pydantic = pydantic_model_creator(User, name="user")
