from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from src.validator import User


r = Router()


def get_primary_router(root) -> Router:
    @r.message(Command('start'))
    async def on_message(message: Message):
        try:
            await root.tasker.add_user(User(
                user_id=message.from_user.id,
                username=message.from_user.username,
            ))
            await message.answer('Welcome to notify bot!')
        except:
            await message.answer('Error on start')

    @r.message(Command('help'))
    async def on_message(message: Message):
        await message.answer('Help msg')

    return r
