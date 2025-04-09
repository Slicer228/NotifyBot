from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.routers.states import del_last_msg
from src.validator import User


_r = Router()


def get_primary_router(root) -> Router:
    @_r.message(Command('start'))
    @del_last_msg(root)
    async def start(message: Message, *args, **kwargs):
        try:
            await root.tasker.add_user(User(
                user_id=message.from_user.id,
                username=message.from_user.username,
            ))
            msg = await message.answer('Welcome to notify bot!')
        except:
            msg = await message.answer('Error on start')
        return msg.message_id

    @_r.message(Command('help'))
    @del_last_msg(root)
    async def help(message: Message, *args, **kwargs):
        msg = await message.answer('Help msg')
        return msg.message_id
    return _r
