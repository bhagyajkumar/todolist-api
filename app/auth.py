import os
import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends, status
from .models import User, user_pydantic
from pydantic import BaseModel
from .exceptions import UserAlreadyExists
from fastapi.security import APIKeyHeader
from datetime import datetime, timedelta
from jose import JWTError

load_dotenv

SECRET_KEY = os.environ["SECRET_KEY"]

jwt_scheme = APIKeyHeader(name="JWT")

router = APIRouter()


class RegisterModel(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


async def get_current_user(token:str = Depends(jwt_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        user = await User.filter(id=user_id).first()
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception
    except:
        raise credentials_exception



@router.post("/register")
async def register_user(data: RegisterModel):
    username = data.username
    password = data.password
    try:
        user = await User.create_user(username=username, password=password)
        print("after user creating", user)
        return await user_pydantic.from_tortoise_orm(user)
    except UserAlreadyExists:
        raise HTTPException(
            status_code=403, detail="a user with same username already exists")
    except:
        return HTTPException(status_code=403, detail="an error has occured")


@router.post("/token", response_model=Token)
async def login_for_access_token(credentials: RegisterModel):
    user = await User.authenticate_user(credentials.username, credentials.password)
    print(user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print(user)
    access_token = await user.create_access_token(type="access")
    refresh_token = await user.create_access_token(expire_minutes=3200, type="refresh")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/protected")
async def test(user: User = Depends(get_current_user)):
    return await user_pydantic.from_tortoise_orm(user)
