from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, CallbackQuery
from src.routers.states import del_last_msg, check_state, DeclineChanges
from src.validator import User


_r = Router()
kb = [
    [
        KeyboardButton(text="Добавить задачу"),
        KeyboardButton(text="Удалить задачу")
    ],
    [
        KeyboardButton(text="Показать мои задачи")
    ]
]
main_menu = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


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
            msg = await message.answer('Welcome to notify bot!', reply_markup=main_menu)
        except:
            msg = await message.answer('Error on start')
        return msg.message_id

    @_r.message(Command('help'))
    @check_state
    @del_last_msg(root)
    async def help(message: Message, *args, **kwargs):
        msg = await message.answer('Help msg')
        return msg.message_id

    @_r.callback_query()
    @del_last_msg(root)
    async def decline(cb: CallbackQuery, state: FSMContext, *args, **kwargs):
        await state.clear()
        msg = await root.send_message(cb.from_user.id, "Действие отменено!")

        return msg.message_id
    return _r
