from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from src.validator import User
from src.routers.states import AddTask


_r = Router()


def get_add_task_router(root) -> Router:

    #@_r.callback_query()
    return _r
