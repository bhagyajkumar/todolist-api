from fastapi import FastAPI
from . import auth, todo
from tortoise.contrib.fastapi import register_tortoise
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.include_router(auth.router)
app.include_router(todo.router)

register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
