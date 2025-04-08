from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from src.validator import User


_r = Router()


def get_add_task_router(root) -> Router:
    return _r
