from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from src.routers.states import del_last_msg, check_state, DeclineChanges, EndChanges
from src.validator import User
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
            msg = await message.answer('Welcome to notify bot!', reply_markup=main_menu_kb)
        except:
            msg = await message.answer('Error on start', reply_markup=main_menu_kb)
        return msg.message_id

    @_r.message(Command('help'))
    @check_state
    @del_last_msg(root)
    async def help(message: Message, *args, **kwargs):
        msg = await message.answer('Help msg', reply_markup=main_menu_kb)
        return msg.message_id

    @_r.callback_query(DeclineChanges.filter())
    @del_last_msg(root)
    async def decline(cb: CallbackQuery, state: FSMContext, *args, **kwargs):
        await state.clear()
        msg = await root.send_message(cb.from_user.id, "Действие отменено!", reply_markup=main_menu_kb)

        return msg.message_id

    @_r.callback_query(EndChanges.filter())
    @del_last_msg(root)
    async def end(cb: CallbackQuery, state: FSMContext, *args, **kwargs):
        await state.clear()
        msg = await root.send_message(cb.from_user.id, "Главное меню", reply_markup=main_menu_kb)

        return msg.message_id
    return _r
