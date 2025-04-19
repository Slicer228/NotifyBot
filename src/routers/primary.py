from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from src.routers.states import del_last_msg, check_state, DeclineChanges
from src.validator import User, MessageObj
from src.routers.buttons import main_menu_kb


_r = Router()


def get_primary_router(root: Bot) -> Router:
    @_r.message(Command('start'))
    @check_state
    @del_last_msg(root)
    async def start(message: Message, *args, **kwargs):
        try:
            await root.tasker.add_user(User(
                user_id=message.from_user.id,
                username=message.from_user.username,
            ))
            return MessageObj(
                text='Welcome to notify bot!',
                kb=main_menu_kb,
                chat_id=message.from_user.id,
            )
        except:
            return MessageObj(
                text='Error on start',
                kb=main_menu_kb,
                chat_id=message.from_user.id,
            )

    @_r.message(Command('help'))
    @check_state
    @del_last_msg(root)
    async def help(message: Message, *args, **kwargs):
        return MessageObj(
            text='Help msg',
            kb=main_menu_kb,
            chat_id=message.from_user.id,
        )

    @_r.callback_query(DeclineChanges.filter())
    @del_last_msg(root)
    async def decline(cb: CallbackQuery, state: FSMContext, *args, **kwargs):
        await state.clear()
        return MessageObj(
            text="Действие отменено!",
            kb=main_menu_kb,
            chat_id=cb.from_user.id,
        )

    return _r
