import os
import jwt
from datetime import datetime, timedelta
from tortoise import fields, models
from passlib.context import CryptContext

from .exceptions import UserAlreadyExists
from tortoise.contrib.pydantic import pydantic_model_creator
from dotenv import load_dotenv
from tortoise import Tortoise

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
        return pwd_context.verify(password, self.password_hash)

    @classmethod
    async def authenticate_user(cls, username, password):
        user = await cls.filter(username=username).first()
        if user is None:
            return False
        if await user.verify_password(password):
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


class Todo(models.Model):
    id = fields.UUIDField(pk=True)
    content = fields.CharField(max_length=200)
    user = fields.ForeignKeyField(
        "models.User", related_name="todos", on_delete=fields.CASCADE)
    is_completed = fields.BooleanField(default=False)

    class PydanticMeta:
        excluded = ["id"]
        include = ["content", "is_completed", "user_id"]


Tortoise.init_models(["app.models"], "models")


user_pydantic = pydantic_model_creator(User, name="user")

Todo_Pydantic = pydantic_model_creator(Todo, name="Todo", include=["id"])
TodoIn_Pydantic = pydantic_model_creator(
    Todo, name="TodoIn", exclude_readonly=True, exclude=["user_id"])
