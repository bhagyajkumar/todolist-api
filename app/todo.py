from fastapi import APIRouter
from fastapi import Depends
from .auth import get_current_user
from .models import Todo, User, Todo_Pydantic, TodoIn_Pydantic
from pydantic import BaseModel

router = APIRouter()

class TodoAddModel(BaseModel):
    content: str
    is_completed: bool


@router.get("/todos", response_model=Todo_Pydantic)
async def get_user_todos(user:User = Depends(get_current_user)):
    todos = await Todo.filter(user=user.id)
    return await Todo_Pydantic.from_queryset(Todo.filter(user=user.id).prefetch_related("user").all())

@router.post("/todos")
async def add_todo(todo: TodoIn_Pydantic, user:User = Depends(get_current_user)):
    todo = await Todo.create(**todo.dict(exclude_unset=True), user=user)
    return await Todo_Pydantic.from_tortoise_orm(todo)

