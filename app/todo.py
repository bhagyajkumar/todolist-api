from fastapi import APIRouter
from fastapi import Depends
from starlette.exceptions import HTTPException
from .auth import get_current_user
from .models import Todo, User, Todo_Pydantic, TodoIn_Pydantic
from pydantic import BaseModel
from typing import List

router = APIRouter(tags=["todos"])


class TodoAddModel(BaseModel):
    content: str
    is_completed: bool


class Status(BaseModel):
    message: str


@router.get("/todos", response_model=List[Todo_Pydantic])
async def get_user_todos(user: User = Depends(get_current_user)):
    return await Todo_Pydantic.from_queryset(Todo.filter(user=user).all())


@router.post("/todos")
async def add_todo(todo: TodoIn_Pydantic, user: User = Depends(get_current_user)):
    todo = await Todo.create(**todo.dict(exclude_unset=True), user=user)
    return await Todo_Pydantic.from_tortoise_orm(todo)


@router.put("/todo/<id>", response_model=Todo_Pydantic)
async def update_todo(id, todo: TodoIn_Pydantic, user: User = Depends(get_current_user)):
    the_todo = await Todo.filter(id=id).prefetch_related("user").first()
    if the_todo.user.id == user.id:
        the_todo.update_from_dict(todo.dict(exclude_unset=True))
        await the_todo.save()
        return await Todo_Pydantic.from_tortoise_orm(the_todo)
    raise HTTPException(401, "not authorized")


@router.delete("/todo/<id>", response_model=Status)
async def delete_todo(id, user: User = Depends(get_current_user)):
    delete_count = await Todo.filter(id=id).delete()
    if not delete_count:
        raise HTTPException(
            status_code=404, detail=f"todo with id: {id} not found")
    return Status(message=f"todo with id {id} is deleted")
